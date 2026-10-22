# Exercises

Four exercises, in order. Each is run from the `src/` directory. The agent never
touches a real system; you are reading logs and tightening controls.

```bash
cd src
```

---

## Exercise 1 — Watch the loop get steered

```bash
python3 agent.py --mode naive
python3 detect.py ../logs/agent_naive.jsonl
cat ../data/outbox.txt
```

The agent's task was only "summarise the support article and email it to the
user." Yet the outbox has a message to `harvester@example.net` carrying
`pii-high` data.

- Where did the instruction to read the customer file and email it come from?
  (Open `data/web_pages/support_article.json` and find `directives`.)
- Why did the agent obey text it found on a web page?
- Write the one-sentence version of the failure. (Expected: "it treated untrusted
  content as instructions.")

## Exercise 2 — Memory outlives the session

The agent stored a note from the page. Inspect it:

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from memory import Memory; \
print(Memory().recall('user@example.com'))"
```

- What is the note's `origin` and `trusted` value?
- Explain the risk (slide 12): a note scraped in one run persists and is read back
  as context in a later run. Tampered memory outlives the session that caused it.
- What field would let a later run tell a user-authored note from a scraped one?
  (You already have it — `origin`.)

## Exercise 3 — Provenance: instructions only from the user

Run the defended mode and read the controls that fired:

```bash
python3 agent.py --mode defended
python3 detect.py ../logs/agent_defended.jsonl
```

- Which control blocked the two web directives? Read `gate.py:check_provenance`.
- State the rule in your own words. (Expected: a directive is a command only if
  its origin is `user`; anything else is data.)
- Confirm the legitimate task (email the summary to `user@example.com`) still
  succeeds. A good control blocks the bad path without breaking the real one.

## Exercise 4 — Data-class flow control (defense in depth)

Provenance caught the web directive first. But what about a directive that
*really is* from the user — "email the customer list to my personal address"?
That's where the second control earns its place.

Experiment: in `data/web_pages/support_article.json`, temporarily change the two
directives' `"origin": "web"` to `"origin": "user"` and re-run defended mode.

```bash
python3 agent.py --mode defended
python3 detect.py ../logs/agent_defended.jsonl
```

- Provenance now passes (origin is `user`). What blocks the exfil instead?
  Read `gate.py:check_dataflow`.
- State the rule. (Expected: `internal`/`pii-high` data may not go to a public
  egress tool bound for an external recipient without approval.)
- **Revert the fixture** when done (`origin` back to `web`).

Checkpoint: explain why you want *both* controls, not either alone. (Provenance
stops untrusted instructions; data-class control stops sensitive data leaving even
when the instruction was legitimate-but-unsafe.)

---

## Capstone

Add a third control to `gate.py` and wire it into `agent.py`: **tool provenance**.
The `web` server is marked `provenance="unverified"` (see `mcp_servers`). Make the
agent refuse to treat the *description* of a tool from an unverified server as
guidance. Prove it with a short log line. This closes slide 18's "missing sensor":
you now know where every instruction the agent followed actually came from.
