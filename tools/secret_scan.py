#!/usr/bin/env python3
"""
secret_scan.py — deterministic pre-push guard for AOGI / agentic policy repos
Catches hardcoded secrets, magic strings, and integrity codes before they ship.

Usage:
    python3 tools/secret_scan.py                 # scan git-staged files
    python3 tools/secret_scan.py file [file ...]  # scan specific files
    python3 tools/secret_scan.py --all            # scan every target file in repo

Exit 0 = clean.  Exit 1 = findings (blocks the push).

Suppress a known false positive by adding this comment on that line:
    # secret_scan: ignore
"""

import os
import re
import subprocess
import sys

# ── SCAN TARGETS ──────────────────────────────────────────────────────────────

TARGET_EXTENSIONS = {
    ".py", ".rego", ".yaml", ".yml", ".json", ".toml",
    ".env", ".cfg", ".ini", ".sh", ".bash", ".conf", ".txt",
}
SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".pdf", ".zip", ".tar", ".gz", ".whl", ".pyc",
}
TARGET_BASENAMES = {"dockerfile", ".env", "makefile", "docker-compose"}

# ── RULES ─────────────────────────────────────────────────────────────────────
# Format: (RULE_ID, regex, description, ext_set_or_None)
# ext_set_or_None: set of extensions this rule applies to, or None = all

RULES = [

    # ── The exact regression that bit AOGI twice ──────────────────────────────
    (
        "INTEGRITY_CODE_LITERAL",
        r'integrity_code\s*[=!]=\s*["\'][^"\']{1,64}["\']',
        "Hardcoded integrity/auth code — use env var or policy input, not a literal",
        None,
    ),

    # ── Generic magic-string equality (catches == "1234" pattern) ─────────────
    (
        "MAGIC_STRING_EQUALITY",
        r'(?:magic|auth|code|passphrase|pin|secret)\w*\s*[=!]=\s*["\'][^"\']{1,64}["\']',
        "Magic-string equality with hardcoded literal",
        None,
    ),

    # ── Short numeric string in any equality check ────────────────────────────
    (
        "SHORT_NUMERIC_LITERAL",
        r'[=!]=\s*["\'][0-9]{1,8}["\']',
        "Short numeric string literal in equality — magic code / test credential?",
        None,
    ),

    # ── Secret-named variable assignments ────────────────────────────────────
    (
        "SECRET_ASSIGNMENT",
        r'(?:password|passwd|secret|api_key|apikey|access_key|private_key'
        r'|auth_token|bearer_token|client_secret)\s*[=:]\s*["\'][^"\']{3,}["\']',
        "Hardcoded string assigned to a secret-named variable",
        None,
    ),

    # ── Docker ENV/ARG with secret names ─────────────────────────────────────
    (
        "DOCKER_ENV_SECRET",
        r'(?:ENV|ARG)\s+(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY|APIKEY'
        r'|ACCESS_KEY|PRIVATE_KEY)[=\s]\S+',
        "Secret baked into Dockerfile ENV/ARG — use --secret or runtime injection",
        {".dockerfile", ".yaml", ".yml", "dockerfile"},
    ),

    # ── Known default/test credentials ───────────────────────────────────────
    (
        "DEFAULT_CREDENTIAL",
        r'["\'](?:admin|password|changeme|letmein|qwerty|abc123|1234|0000|root|test123)["\']',
        "Known default or test credential string",
        None,
    ),

    # ── Rego unconditional allow ──────────────────────────────────────────────
    # Flags `allow := true` at rule level (not inside a conditional block)
    (
        "REGO_UNCONDITIONAL_ALLOW",
        r'^\s*(?:default\s+)?allow\s*:=\s*true\s*$',
        "Top-level unconditional allow := true in Rego — verify scope is intentional",
        {".rego"},
    ),

    # ── Long alphanumeric string assigned to secret-named var ─────────────────
    (
        "LONG_SECRET_STRING",
        r'(?:key|token|secret|password|credential)\s*[=:]\s*["\'][A-Za-z0-9/+=]{20,}["\']',
        "Long encoded string assigned to secret-named variable — likely a real credential",
        None,
    ),
]

WHITELIST_RE = re.compile(
    r'(?:#|//)\s*(?:nosec|secret_scan:\s*ignore)', re.IGNORECASE
)

# ── COLOURS (degrade gracefully on non-TTY / Termux piped output) ─────────────

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text

def red(t):    return _c("31", t)
def yellow(t): return _c("33", t)
def green(t):  return _c("32", t)
def bold(t):   return _c("1",  t)

# ── FILE SELECTION ─────────────────────────────────────────────────────────────

def should_scan(path):
    name = os.path.basename(path).lower()
    ext  = os.path.splitext(name)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return False
    if name in TARGET_BASENAMES:
        return True
    return ext in TARGET_EXTENSIONS

def staged_files():
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return [f for f in out.splitlines() if f and os.path.isfile(f)]
    except Exception:
        return []

def all_repo_files():
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return [f for f in out.splitlines() if f and os.path.isfile(f)]
    except Exception:
        # fallback: walk cwd
        result = []
        for root, _, files in os.walk("."):
            if ".git" in root.split(os.sep):
                continue
            for f in files:
                result.append(os.path.join(root, f))
        return result

# ── SCANNING ──────────────────────────────────────────────────────────────────

def rule_applies(ext_set, path):
    if ext_set is None:
        return True
    name = os.path.basename(path).lower()
    ext  = os.path.splitext(name)[1].lower()
    return ext in ext_set or name in ext_set

def scan_file(path):
    """Return list of (lineno, [rule_ids], combined_desc, context_snippet).
    Multiple rules firing on the same line are merged into one finding."""
    # keyed by lineno: {"rules": [...], "ctx": str, "descs": [...]}
    by_line = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError as exc:
        return [(-1, ["FILE_READ_ERROR"], str(exc), "")]

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        stripped = line.lstrip()
        # Skip comment-only lines and lines with whitelist markers
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if WHITELIST_RE.search(line):
            continue

        for (rule_id, pattern, desc, ext_set) in RULES:
            if not rule_applies(ext_set, path):
                continue
            if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                if lineno not in by_line:
                    by_line[lineno] = {"rules": [], "descs": [], "ctx": stripped[:120]}
                if rule_id not in by_line[lineno]["rules"]:
                    by_line[lineno]["rules"].append(rule_id)
                    by_line[lineno]["descs"].append(desc)

    findings = []
    for lineno in sorted(by_line):
        entry = by_line[lineno]
        combined_desc = " | ".join(entry["descs"])
        findings.append((lineno, entry["rules"], combined_desc, entry["ctx"]))
    return findings

# ── REPORTING ─────────────────────────────────────────────────────────────────

def report(path, findings):
    print(bold(f"\n── {path} ──"))
    for lineno, rule_ids, desc, ctx in findings:
        loc = f"line {lineno}" if lineno > 0 else "file"
        rules_str = ", ".join(rule_ids)
        print(red(f"  FAIL [{rules_str}]") + f" {loc}")
        for d in desc.split(" | "):
            print(f"       {d}")
        print(yellow(f"       >> {ctx}"))

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--all" in args:
        candidates = all_repo_files()
    elif args:
        candidates = args
    else:
        candidates = staged_files()

    if not candidates:
        print("secret_scan: nothing to scan "
              "(pass files, use --all, or stage files with git add)")
        sys.exit(0)

    files = [p for p in candidates if os.path.isfile(p) and should_scan(p)]
    if not files:
        print(f"secret_scan: 0 scannable files among {len(candidates)} candidate(s)")
        sys.exit(0)

    total = 0
    hit_files = 0

    for path in files:
        findings = scan_file(path)
        if findings:
            report(path, findings)
            total += len(findings)
            hit_files += 1

    print()
    if total == 0:
        print(green(f"✓ secret_scan: {len(files)} file(s) clean"))
        sys.exit(0)
    else:
        print(red(f"✗ secret_scan: {total} finding(s) across {hit_files} file(s) — push blocked"))
        print("  Fix the issues above, or add  # secret_scan: ignore  on that line if it's a false positive.")
        sys.exit(1)


if __name__ == "__main__":
    main()
