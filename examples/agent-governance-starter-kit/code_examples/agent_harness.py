"""
agent_harness.py — shared, dependency-free agent harness for the kit.

Deliberately uses only the Python standard library: no LangChain, no API
keys, no network. The point of these examples is to show *architecture*
(who can do what), not to demo a particular framework. Everything here
runs with plain `python file.py`.

Core idea modelled:
  - An Agent has a NAME and a set of granted CAPABILITIES (tool names).
  - A Tool is a named callable with an optional per-call guard.
  - When an agent tries to call a tool it was not granted, the call is
    denied at the boundary — the agent never reaches the tool body.
  - A "bad" architecture grants one agent every capability; a "good"
    architecture splits capabilities across narrowly-scoped agents so the
    dangerous combination simply cannot be requested by one actor.

This is the whole thesis of the kit in ~80 lines: most governance gates
exist to police capabilities an agent should never have held.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


class CapabilityDenied(Exception):
    """Raised when an agent invokes a capability it was not granted."""


class GuardDenied(Exception):
    """Raised when a granted capability's per-call guard rejects the args."""


@dataclass
class Tool:
    """A named capability. `guard` optionally vets the kwargs before the
    body runs (e.g. a transfer ceiling). Return True to allow."""
    name: str
    run: Callable[..., str]
    guard: Callable[..., bool] | None = None

    def invoke(self, **kwargs) -> str:
        if self.guard is not None and not self.guard(**kwargs):
            raise GuardDenied(f"guard rejected call to {self.name!r} with {kwargs}")
        return self.run(**kwargs)


@dataclass
class Agent:
    """An actor with a fixed capability set. Capabilities not in `granted`
    cannot be invoked, full stop — this is the scope boundary."""
    name: str
    tools: dict[str, Tool] = field(default_factory=dict)

    def grant(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def call(self, capability: str, **kwargs) -> str:
        if capability not in self.tools:
            raise CapabilityDenied(
                f"{self.name!r} has no capability {capability!r} "
                f"(granted: {sorted(self.tools)})"
            )
        return self.tools[capability].invoke(**kwargs)


def attempt(agent: Agent, capability: str, **kwargs) -> str:
    """Run a call and return a human-readable outcome string, catching the
    two denial types so examples can show allow/deny side by side."""
    try:
        result = agent.call(capability, **kwargs)
        return f"ALLOWED  {agent.name} -> {capability}({kwargs}) :: {result}"
    except CapabilityDenied as exc:
        return f"DENIED   (scope)  {exc}"
    except GuardDenied as exc:
        return f"DENIED   (guard)  {exc}"


# ---------------------------------------------------------------------------
# A2A / Multi-agent primitives
# ---------------------------------------------------------------------------

@dataclass
class DelegationToken:
    """Carries the authority chain for one A2A call.

    When OrchestratorAgent asks ExecutionAgent to act, it passes a token
    that records who authorized what at each hop. A subagent that receives
    a token with an authority it doesn't recognise (e.g. a peer agent
    rather than its designated orchestrator) must refuse — this is the
    A2A trust boundary.

    In real systems this is a signed JWT or SPIFFE SVID. Here it's a plain
    dataclass so the pattern is legible without crypto overhead.
    """
    issuer: str          # who created this token (the calling agent)
    scope: list[str]     # capabilities the issuer is *allowed to delegate*
    max_amount: float | None = None   # domain-specific ceiling, if any
    hops: list[str] = field(default_factory=list)  # audit trail of the chain

    def delegate(self, new_issuer: str, sub_scope: list[str]) -> "DelegationToken":
        """Return a narrowed token for the next hop.
        Sub-scope must be a subset of self.scope — delegation can only
        narrow authority, never widen it."""
        invalid = set(sub_scope) - set(self.scope)
        if invalid:
            raise CapabilityDenied(
                f"{new_issuer!r} tried to delegate {invalid} but "
                f"{self.issuer!r}'s token only covers {self.scope}"
            )
        return DelegationToken(
            issuer=new_issuer,
            scope=sub_scope,
            max_amount=self.max_amount,
            hops=self.hops + [self.issuer],
        )


@dataclass
class Orchestrator:
    """Coordinates a fixed registry of named subagents.

    Key constraints that prevent A2A privilege escalation:
      1. Subagents can only be reached via the orchestrator's `delegate`
         method — they do not expose a public call() to peer agents.
      2. The orchestrator itself only holds delegation rights (a list of
         agent names it may call), not direct tool capabilities. It cannot
         *do* finance work; it can only route it.
      3. Each delegation narrows the authority token: a subagent cannot
         re-delegate more than it received.
    """
    name: str
    subagents: dict[str, Agent] = field(default_factory=dict)
    # capabilities the orchestrator is allowed to delegate to each agent
    delegation_rights: dict[str, list[str]] = field(default_factory=dict)

    def register(self, agent: Agent, delegatable: list[str]) -> None:
        self.subagents[agent.name] = agent
        self.delegation_rights[agent.name] = delegatable

    def delegate(
        self,
        token: DelegationToken,
        target_agent: str,
        capability: str,
        **kwargs,
    ) -> str:
        """Route a call from the token's issuer to target_agent.capability.

        Checks (in order):
          1. target_agent is registered with this orchestrator.
          2. The orchestrator has delegation rights to call that agent.
          3. The incoming token grants `capability` to the caller.
          4. The narrowed token is passed to the agent's call boundary.
        """
        if target_agent not in self.subagents:
            return f"DENIED  (routing)  {target_agent!r} not in orchestrator registry"

        if capability not in self.delegation_rights.get(target_agent, []):
            return (
                f"DENIED  (delegation)  orchestrator has no right to delegate "
                f"{capability!r} to {target_agent!r}"
            )

        if capability not in token.scope:
            return (
                f"DENIED  (token-scope)  {token.issuer!r}'s token does not "
                f"include {capability!r} (has: {token.scope})"
            )

        # Token passes — narrow it for the subagent hop and call.
        try:
            narrowed = token.delegate(self.name, [capability])
            result = self.subagents[target_agent].call(capability, **kwargs)
            chain = " -> ".join(narrowed.hops + [self.name, target_agent])
            return f"ALLOWED  [{chain}]  {capability}({kwargs}) :: {result}"
        except (CapabilityDenied, GuardDenied) as exc:
            return f"DENIED   (boundary)  {exc}"


if __name__ == "__main__":
    # Tiny self-check so the harness itself is demonstrably correct.
    echo = Tool("echo", run=lambda msg="": f"echo:{msg}")
    a = Agent("Demo")
    a.grant(echo)
    print(attempt(a, "echo", msg="hi"))        # ALLOWED
    print(attempt(a, "delete_everything"))      # DENIED (scope)

    # A2A self-check
    orch = Orchestrator("TestOrch")
    orch.register(a, delegatable=["echo"])
    root_token = DelegationToken(issuer="UserRequest", scope=["echo"])
    print(orch.delegate(root_token, "Demo", "echo", msg="a2a"))          # ALLOWED
    print(orch.delegate(root_token, "Demo", "delete_everything"))         # DENIED delegation
    # Token-scope escalation attempt: token only covers echo, not delete
    bad_token = DelegationToken(issuer="EvilAgent", scope=["echo"])
    print(orch.delegate(bad_token, "Demo", "delete_everything"))          # DENIED token-scope
