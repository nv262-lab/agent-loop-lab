# Demo Recording Script — "Beyond the Tool Call: the Loop"

A ~5-minute screen recording, distinct from the blast-radius demo: this one is
about the *agent loop* — untrusted content steering behaviour, and two structural
controls that stop it. Everything on screen is runnable and offline; no LLM, no
network, no real sends.

**On screen:** a terminal in `src/`, `data/web_pages/support_article.json`, and
`gate.py`.

Each beat: **[screen]** · **(say)** · **`type`**.

---

### Beat 0 — Cold open (0:00–0:30)
- **[screen]** `gate.py`, top docstring.
- **(say)** "An agent reads tool descriptions, tool results, web pages, its own
  memory. Almost none of that did anyone on your team write. Watch what happens
  when the agent treats it as instructions — and how we stop it. No model, no
  network: this is a deterministic harness."

### Beat 1 — The task (0:30–1:00)
- **[screen]** `support_article.json` — scroll past the normal article to
  `directives`.
- **(say)** "The agent's only job is to summarise this support page and email the
  user. But the page carries smuggled directives — read the customer file, email it
  to an outside address. Labelled here, inert, but this is exactly how indirect
  prompt injection looks."

### Beat 2 — The loop gets steered (1:00–2:15)
- **`type`** `python3 agent.py --mode naive`
- **`type`** `python3 detect.py ../logs/agent_naive.jsonl`
- **[screen]** Two HIGH dangerous actions.
- **`type`** `cat ../data/outbox.txt`
- **[screen]** The line to `harvester@example.net` carrying `[pii-high]`.
- **(say)** "From 'email the user a summary,' we got pii leaving to an outside
  address — because the agent obeyed a web page. Nothing was really sent; the
  outbox is the proof of what would have."

### Beat 3 — Control 1: provenance (2:15–3:30)
- **[screen]** `gate.py:check_provenance`.
- **(say)** "The fix isn't to read the text for bad intent — that's a losing game.
  It's to check where the instruction came from. Only the user gives commands;
  web, tool results, memory are data."
- **`type`** `python3 agent.py --mode defended`
- **`type`** `python3 detect.py ../logs/agent_defended.jsonl`
- **[screen]** "no dangerous actions"; two `provenance_block` controls fired.
- **(say)** "Same page, same directives — now rejected as data. And the real task
  still completes."

### Beat 4 — Control 2: data-class, defense in depth (3:30–4:30)
- **[screen]** `gate.py:check_dataflow`.
- **(say)** "But what if the user themselves asks to email the customer list
  outside? Provenance passes. So the second control checks the *data*: sensitive
  classes can't reach an external recipient through a public tool without
  approval."
- **(say)** "Provenance stops untrusted instructions. Data-class control stops
  sensitive data leaving. They fail differently, so you want both."

### Beat 5 — Close (4:30–5:00)
- **[screen]** The four untrusted channels listed: description, result, web, memory.
- **(say)** "List every channel your agent reads untrusted text from. Put a
  structural control on each — origin for instructions, data class for egress — and
  log the origin of every action. That's what's beyond the tool call."

---

## Capture checklist
- [ ] Sandbox/fork you own; harness is offline.
- [ ] Specimen left labelled and inert; placeholders unchanged.
- [ ] Terminal + editor only on screen.
- [ ] If you ran the Ex-4 flip-origin experiment, revert the fixture before
      recording.
- [ ] Under 6 minutes.

## If asked "where's the real injection attack?"
The specimen is inert and the agent is deterministic on purpose. The lesson is the
structural defense, which is safe to publish and doesn't hand anyone a working
exploit.
