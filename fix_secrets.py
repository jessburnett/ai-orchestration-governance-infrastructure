import re, pathlib

def replace(path, old, new):
    p = pathlib.Path(path)
    text = p.read_text()
    assert old in text, f"pattern not found in {path}"
    p.write_text(text.replace(old, new))
    print(f"fixed: {path}")

replace("aogi/common.py",
    'API_KEY = os.getenv("HUB_API_KEY", "agt-secret-key-2024")',
    'API_KEY = os.environ["HUB_API_KEY"]  # no default — must be set explicitly, never falls back to a known value')

replace("aogi/ecosystem_hub.py",
    'API_KEY = os.getenv("HUB_API_KEY", "agt-secret-key-2024")',
    'API_KEY = os.environ["HUB_API_KEY"]  # no default — server refuses to start with a known/guessable key')

p = pathlib.Path("aogi/langchain_governance.py")
t = p.read_text()
t = t.replace('os.getenv("HUB_API_KEY", "agt-secret-key-2024")', 'os.environ["HUB_API_KEY"]')
p.write_text(t)
print("fixed: aogi/langchain_governance.py")

p = pathlib.Path("docker-compose.yml")
t = p.read_text()
t = t.replace('HUB_API_KEY=agt-secret-key-2024',
              'HUB_API_KEY=${HUB_API_KEY:?Set HUB_API_KEY in your .env file, see .env.example}')
p.write_text(t)
print("fixed: docker-compose.yml")

replace("tests/test_governance.py",
    'API_KEY = "agt-secret-key-2024" # Default for testing',
    'API_KEY = "test-only-dummy-key-not-for-production"  # fixture value for the test client; app sets HUB_API_KEY via env, no default')

replace("README.md",
    '## 🚀 Getting Started\nEnsure your API Key is set in the environment:\n```bash\nexport HUB_API_KEY="agt-secret-key-2026"\ndocker compose up --build\n```',
    '## 🚀 Getting Started\nGenerate your own local API key — never reuse a value from documentation or another deployment:\n```bash\ncp .env.example .env\necho "HUB_API_KEY=$(openssl rand -hex 32)" >> .env\ndocker compose up --build\n```')

replace("README.md",
    'export HUB_API_KEY="agt-secret-key-2026"\n./scripts/start_stack.sh',
    'export HUB_API_KEY=$(openssl rand -hex 32)\n./scripts/start_stack.sh')

pathlib.Path(".env.example").write_text(
    "# Copy this file to .env and set your own value — .env is gitignored.\n"
    "# Generate a real local-dev key, e.g.:  openssl rand -hex 32\n"
    "HUB_API_KEY=\n")
print("created: .env.example")

with open(".gitignore", "a") as f:
    f.write("\n# Local secrets — never commit real credentials\n.env\n")
print("updated: .gitignore")

print("\nAll fixes applied.")
