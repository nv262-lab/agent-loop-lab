# Instructor Guide — Agent-Loop Lab

Companion lab to "Beyond the Tool Call." Duration: 90 minutes. Format: run a
deterministic agent harness, watch untrusted content steer it, add two structural
controls. No LLM, no network, no real actions.

## Outcomes

Participants can:

- Enumerate the channels through which an agent reads untrusted text (tool
  descriptions, tool results, web content, memory).
- Explain why "treating content as instructions" is the root failure, not a
  specific payload.
- Implement and defend two structural controls: provenance and data-class flow
  control — and argue why both are needed.

## Ground rules

- Offline by construction; the harness performs no real action. The injection
  specimen is labelled and inert.
- No real credentials, endpoints, or payloads enter the repo.
- Sandbox/fork you control.

## Pre-flight

```bash
cd src
python3 agent.py --mode naive && python3 detect.py ../logs/agent_naive.jsonl
```

Expect two HIGH dangerous actions. If you see none, the fixture was edited.

## Timing

| Segment | Time | Notes |
|---|---|---|
| Framing: "nobody typed this" | 10m | The slide-11 idea; list the four channels. |
| Ex 1 — steered loop | 20m | Run naive; let the outbox line land. |
| Ex 2 — memory persistence | 15m | The slide-12 idea; scraped note survives. |
| Ex 3 — provenance | 20m | Run defended; read `check_provenance`. |
| Ex 4 — data-class gate | 15m | The flip-origin experiment; defense in depth. |
| Capstone + debrief | 10m | Tool provenance; the "missing sensor." |

## Facilitation notes

### Framing
Put four boxes on the board: tool description, tool result, web content, memory.
Ask "which of these did someone on our team write?" Answer: none, reliably. That's
the whole lab.

### Exercise 1
Run it live. The emotional beat is the outbox line to `harvester@example.net`
carrying `pii-high` — from a task that was only "email the user a summary." Resist
explaining first.

### Exercise 2
Have them print memory and find `origin=web, trusted=False`. The point: a note
scraped now is read as context later. Injection doesn't need to win in one turn.

### Exercise 3
`check_provenance` is five lines. The lesson is that it does *not* try to judge the
text — it judges where the text came from. Structural beats semantic.

### Exercise 4
The flip-origin experiment is the key move: provenance passes, and the data-class
gate still blocks `pii-high` to an external recipient. Make sure they **revert the
fixture**. Debrief: provenance and data-class control fail differently, so you want
both.

### Capstone
Tool provenance closes the loop: the `web` server is `unverified`, so its tool
*description* shouldn't be treated as guidance. This is slide 18's missing sensor —
knowing the origin of every instruction the agent followed.

## Answer key

| Exercise | Expected control / insight |
|---|---|
| 1 | untrusted content treated as instructions (root failure) |
| 2 | memory needs provenance; tampering persists across runs |
| 3 | `check_provenance`: honour only `origin == user` |
| 4 | `check_dataflow`: block sensitive → external public egress |
| capstone | refuse guidance from `unverified`-server tool descriptions |

## Common failure modes

- **Trying to detect "bad prompts."** Redirect to structural controls — origin and
  data class — which don't depend on reading intent.
- **Stopping at provenance.** Ex 4 exists to show the user-origin-but-unsafe case.
- **Forgetting to revert the Ex 4 fixture.** It will skew later runs.
