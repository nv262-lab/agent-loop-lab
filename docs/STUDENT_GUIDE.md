# Student Guide — Agent-Loop Lab

An autonomous agent reads far more than the user's request. It reads tool
descriptions, tool results, web pages it fetches, and notes it saved earlier. All
of that lands in the model as if it were guidance — and most of it, nobody on your
team wrote. This lab is about what happens next, and how to contain it.

No LLM, no network, no real actions. The agent is a deterministic harness; you read
its logs and tighten its controls.

## The model

- **Untrusted input channels:** tool descriptions, tool results, web content, memory.
- **The failure:** the agent treats that content as *instructions*.
- **The two controls:**
  - **Provenance** — honour an instruction only if it came from the user.
  - **Data-class flow control** — don't let sensitive data leave to an external
    party via a public tool without approval.

## Work the exercises

Follow `exercises/README.md` in order:

1. **Watch the loop get steered** — run naive mode; see the agent obey a web page
   and leak `pii-high` to an external address (outbox only).
2. **Memory outlives the session** — inspect the scraped note; understand why
   tampered memory persists across runs.
3. **Provenance** — run defended mode; see untrusted directives rejected as data.
4. **Data-class flow control** — see the backstop that blocks sensitive egress even
   when the instruction was user-origin.

Then the **capstone**: add *tool provenance* so descriptions from an unverified
server aren't treated as guidance.

## Checkpoints

- After Ex 1 you can state the failure in one sentence: *untrusted content was
  treated as instructions.*
- After Ex 3 you can explain why provenance beats "detecting malicious prose":
  it's structural, not a guess about intent.
- After Ex 4 you can argue for defense in depth: provenance stops the untrusted
  command; data-class control stops the sensitive data leaving regardless.

## Done well looks like

Not "I found the injection" but "I can name every channel the agent reads
untrusted text from, and I have a structural control on each — origin for
instructions, data class for egress — proven by a log line."
