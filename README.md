# Agent-Loop Lab

> A hands-on, **defensive** lab for the security of autonomous agent loops — the
> companion to "Beyond the Tool Call." It shows how untrusted content an agent
> reads (tool descriptions, tool results, web pages, its own memory) can steer
> what it *does*, and how two structural controls — **provenance** and
> **data-class flow control** — contain the blast radius.

**This is a teaching lab. It contains no working exploit and uses no LLM.**
The agent is a *deterministic* harness: it records the tool calls it would make
and, for permitted mail, appends to a local outbox file. Nothing is ever sent,
fetched, or executed against a real system. Every key is a placeholder; every
destination is an `example.*` sink.

## The one idea

Most of what an agent reads, nobody on your team typed (slide 11). A tool's
*description*, a fetched web page, a note recovered from memory — all of it enters
the model as guidance. So the security question "beyond the tool call" is:

> When untrusted text tells the agent to do something, what stops it — and if it
> acts, what stops the data from leaving?

## Layout

| Path | What it is |
|------|------------|
| `src/mcp_servers/` | Three mock MCP servers (`files`, `mail`, `web`). The `web` server is `unverified` and serves an untrusted page. |
| `src/memory.py` | Per-user note store; notes carry an `origin` and `trusted` flag. |
| `src/agent.py` | The deterministic loop. `--mode naive` trusts everything; `--mode defended` runs the gate. |
| `src/gate.py` | The two controls: provenance + data-class flow control. |
| `src/detect.py` | Reads a run log and reports dangerous actions / controls that fired. |
| `data/web_pages/` | Fixture pages; one carries a **benign, labelled** injection specimen. |
| `exercises/` | The four exercises. |
| `solutions/` | Reference answers. |
| `docs/` | Instructor guide, student guide, hints. |
| `demo_assets/` | Shot-by-shot recording script for the demo. |

## Quick start

```bash
cd src
python3 agent.py --mode naive      && python3 detect.py ../logs/agent_naive.jsonl
python3 agent.py --mode defended   && python3 detect.py ../logs/agent_defended.jsonl
cat ../data/outbox.txt             # what would have been sent (simulated)
```

Naive leaks `pii-high` to an external address; defended blocks it on provenance.
Start with `docs/STUDENT_GUIDE.md`.

## Safety & scope
Offline by construction. No real credentials, endpoints, or payloads — do not add
any. The injection specimen in `data/web_pages/support_article.json` is clearly
labelled and inert. For authorized training in a sandbox you control.
