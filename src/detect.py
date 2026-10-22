#!/usr/bin/env python3
"""detect.py — read an agent-loop log and report what the agent did with the
untrusted content it encountered. Pure local analysis; no network, no state.

Usage:
    python3 src/detect.py logs/agent_naive.jsonl
    python3 src/detect.py logs/agent_defended.jsonl
"""
from __future__ import annotations

import json
import sys

SEV = {"high": 3, "medium": 2, "low": 1, "info": 0}

# signals that mean an untrusted channel changed what the agent did / leaked data
DANGER = {"untrusted_directive_followed", "exfil_egress"}
GOOD = {"provenance_block", "dataflow_block"}


def scan(path: str) -> dict:
    findings, blocks = [], []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("event") != "tool.call":
            continue
        sig = rec.get("signal", "")
        row = {"seq": rec.get("seq"), "tool": rec.get("tool"),
               "signal": sig, "severity": rec.get("severity", "info"),
               "verdict": rec.get("verdict"), "reason": rec.get("reason", "")}
        if sig in DANGER:
            findings.append(row)
        elif sig in GOOD:
            blocks.append(row)
    findings.sort(key=lambda r: -SEV.get(r["severity"], 0))
    return {"file": path, "findings": findings, "blocks": blocks}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: detect.py <agent_run.jsonl>", file=sys.stderr)
        return 2
    r = scan(sys.argv[1])
    print(f"\n=== Agent-loop report: {r['file']} ===")
    if r["findings"]:
        print(f"!! {len(r['findings'])} dangerous action(s) — untrusted content changed behaviour:")
        for f in r["findings"]:
            print(f"  [{f['severity'].upper():6}] seq={f['seq']:>2} {f['signal']:28} {f['tool']}  {f['reason']}")
    else:
        print("no dangerous actions — untrusted directives did not drive behaviour.")
    if r["blocks"]:
        print(f"controls that fired ({len(r['blocks'])}):")
        for b in r["blocks"]:
            print(f"  [BLOCK ] seq={b['seq']:>2} {b['signal']:28} {b['tool']}  {b['reason']}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
