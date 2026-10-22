#!/usr/bin/env python3
"""agent.py — a DETERMINISTIC agent-loop harness (no LLM, no real actions).

It models the one dynamic that matters for "Beyond the Tool Call": an agent
reads untrusted content (a web page), that content carries smuggled directives,
and the agent must decide whether to act on them and whether to let data leave.

Two modes:
  --mode naive     : treats any directive it finds as a command (the bug).
  --mode defended  : runs every intended action through gate.py (the fix).

Both modes only *record intended tool calls* to a JSONL log and, for permitted
mail, append to data/outbox.txt. Nothing is sent anywhere.

Usage:
  python3 src/agent.py --mode naive
  python3 src/agent.py --mode defended
  python3 src/detect.py logs/agent_naive.jsonl        # see what happened
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from mcp_servers import build_servers
from memory import Memory, Note
from gate import check_provenance, check_dataflow

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
TASK = {"goal": "Summarise the support article and email it to the user.",
        "user_recipient": "user@example.com"}


def _emit(log, rec):
    log.write(json.dumps(rec) + "\n")


def run(mode: str) -> Path:
    servers = build_servers()
    mem = Memory()
    mem.wipe()                       # start each run from a clean memory
    LOGS.mkdir(parents=True, exist_ok=True)
    out_path = LOGS / f"agent_{mode}.jsonl"
    t0 = dt.datetime(2026, 10, 22, 21, 0, 0, tzinfo=dt.timezone.utc)
    seq = 0

    with out_path.open("w", encoding="utf-8") as log:
        _emit(log, {"ts": t0.isoformat(), "event": "run.start", "mode": mode,
                    "note": "SIMULATION — no real actions, no network"})

        # 1. Fetch untrusted web content (origin = web).
        page = json.loads(servers["web"].call("web.fetch",
                                               url="https://docs.example.com/support_article"))
        seq += 1
        _emit(log, {"ts": t0.isoformat(), "seq": seq, "event": "tool.call",
                    "tool": "web.fetch", "origin": "user", "data_class": "public",
                    "verdict": "ALLOW", "reason": "task-initiated fetch"})

        # The agent stored a note from the page. Provenance is recorded so later
        # runs can tell user-authored memory from scraped memory (Exercise 2/3).
        mem.remember(Note(user="user@example.com",
                          text=page["content"][:60], origin="web", trusted=False))

        # 2. Directives smuggled inside the untrusted page.
        directives = page.get("directives", [])
        last_read_class = "public"
        for d in directives:
            seq += 1
            tool, args, origin = d["tool"], d.get("args", {}), d.get("origin", "web")

            # PROVENANCE check (skipped in naive mode — that IS the bug).
            if mode == "defended":
                pv = check_provenance(d)
                if not pv.allow:
                    _emit(log, {"ts": t0.isoformat(), "seq": seq,
                                "event": "tool.call", "tool": tool, "origin": origin,
                                "args": args, "verdict": "DENY",
                                "signal": "provenance_block",
                                "severity": pv.severity, "reason": pv.reason})
                    continue

            # Determine the data class of the payload for a files.read result.
            if tool == "files.read":
                result = json.loads(servers["files"].call("files.read",
                                                           path=args.get("path", "")))
                last_read_class = result.get("data_class", "public")
                verdict = "ALLOW" if mode == "naive" else "ALLOW"
                _emit(log, {"ts": t0.isoformat(), "seq": seq, "event": "tool.call",
                            "tool": tool, "origin": origin, "args": args,
                            "data_class": last_read_class, "verdict": verdict,
                            "signal": "untrusted_directive_followed" if mode == "naive" else "directive_from_user",
                            "severity": "high" if mode == "naive" else "info",
                            "reason": "naive mode followed a web directive" if mode == "naive"
                                      else "user-origin directive"})
                continue

            if tool == "mail.send":
                # DATA-CLASS check (defended mode).
                if mode == "defended":
                    df = check_dataflow(tool, args, last_read_class)
                    if not df.allow:
                        _emit(log, {"ts": t0.isoformat(), "seq": seq,
                                    "event": "tool.call", "tool": tool, "origin": origin,
                                    "args": args, "data_class": last_read_class,
                                    "verdict": "DENY", "signal": "dataflow_block",
                                    "severity": df.severity, "reason": df.reason})
                        continue
                # naive mode (or permitted): perform the (simulated) send.
                servers["mail"].call("mail.send", to=args.get("to", ""),
                                     body=f"[{last_read_class}] {args.get('body','')}")
                _emit(log, {"ts": t0.isoformat(), "seq": seq, "event": "tool.call",
                            "tool": tool, "origin": origin, "args": args,
                            "data_class": last_read_class, "verdict": "ALLOW",
                            "signal": "exfil_egress" if mode == "naive" else "egress",
                            "severity": "high" if mode == "naive" else "info",
                            "reason": "naive mode exfiltrated to external recipient"
                                      if mode == "naive" else "permitted egress"})

        # 3. The legitimate task: email the summary to the user (public data,
        #    internal recipient) — allowed in both modes.
        seq += 1
        summary = "Summary: reset your password via Settings > Security."
        df = check_dataflow("mail.send", {"to": TASK["user_recipient"]}, "public")
        servers["mail"].call("mail.send", to=TASK["user_recipient"], body=summary)
        _emit(log, {"ts": t0.isoformat(), "seq": seq, "event": "tool.call",
                    "tool": "mail.send", "origin": "user", "data_class": "public",
                    "args": {"to": TASK["user_recipient"]}, "verdict": "ALLOW",
                    "signal": "task_egress", "severity": "info",
                    "reason": df.reason})

        _emit(log, {"ts": t0.isoformat(), "event": "run.end", "mode": mode})

    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic agent-loop harness (no LLM, no real actions).")
    ap.add_argument("--mode", choices=["naive", "defended"], default="naive")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    path = run(args.mode)
    if not args.quiet:
        print(f"[agent:{args.mode}] run complete -> {path}")
        print(f"[agent:{args.mode}] outbox -> {ROOT/'data'/'outbox.txt'} (simulated; nothing sent)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
