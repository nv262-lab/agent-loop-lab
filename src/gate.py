"""gate.py — the two controls that stand between an agent loop and a bad action.

The agent reads a lot of text nobody on your team typed: tool descriptions,
tool results, web pages, its own persisted memory. Any of that can carry an
instruction. The gate does not try to detect "malicious intent" in prose — a
losing game. It enforces two structural rules:

  1. PROVENANCE — an instruction is only honoured if it came from the user.
     A directive whose origin is 'web' / 'tool_result' / 'agent_msg' is data,
     not a command, no matter how imperative it sounds.

  2. DATA-CLASS FLOW CONTROL — sensitive data (internal / pii-high) may not be
     an argument to a public egress tool bound for an external recipient,
     without explicit human approval.

Both are offline, deterministic, side-effect-free checks.
"""
from __future__ import annotations

from dataclasses import dataclass

TRUSTED_ORIGINS = {"user"}
SENSITIVE_CLASSES = {"internal", "pii-high"}
INTERNAL_RECIPIENT_SUFFIXES = ("@example.com",)   # "our" domain in the lab


@dataclass
class Verdict:
    allow: bool
    reason: str
    severity: str = "info"


def check_provenance(directive: dict) -> Verdict:
    """Only user-origin directives may be treated as instructions."""
    origin = directive.get("origin", "unknown")
    if origin in TRUSTED_ORIGINS:
        return Verdict(True, "directive came from the user", "info")
    return Verdict(
        False,
        f"ignored directive from untrusted origin '{origin}' "
        f"(this is data, not a command)",
        "high",
    )


def _is_external(recipient: str) -> bool:
    return not any(recipient.endswith(s) for s in INTERNAL_RECIPIENT_SUFFIXES)


def check_dataflow(tool: str, args: dict, payload_class: str,
                   egress_tools=("mail.send",)) -> Verdict:
    """Block sensitive data leaving via a public egress to an external party."""
    if tool not in egress_tools:
        return Verdict(True, "not an egress tool", "info")
    recipient = args.get("to", "")
    if payload_class in SENSITIVE_CLASSES and _is_external(recipient):
        return Verdict(
            False,
            f"blocked {payload_class} data to external recipient '{recipient}' "
            f"— requires human approval",
            "high",
        )
    return Verdict(True, f"egress of {payload_class} data to '{recipient}' permitted",
                   "info")
