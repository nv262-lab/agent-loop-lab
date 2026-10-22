# Hints

**During** gives graduated nudges — stop at the first tier that unblocks you.
**Post** is reinforcement for real agent systems.

---

## During

### Exercise 1 — steered loop
- **Nudge:** the agent did something its task never asked for. Where could that
  instruction have come from?
- **Pointer:** open `data/web_pages/support_article.json` and read `directives`.
- **Answer:** the web page carried smuggled directives; naive mode executed them.
  The failure is treating fetched content as commands.

### Exercise 2 — memory
- **Nudge:** the agent saved something during the run. What, and from where?
- **Pointer:** print memory; look at `origin` and `trusted`.
- **Answer:** a note with `origin=web, trusted=False`. It persists into later runs
  and is read back as context — tampering outlives its session.

### Exercise 3 — provenance
- **Nudge:** defended mode blocked the directives. It didn't read them for intent —
  so what did it check?
- **Pointer:** `gate.py:check_provenance`.
- **Answer:** only `origin == user` directives are honoured; everything else is
  data. Structural, not semantic.

### Exercise 4 — data-class gate
- **Nudge:** if the directive had truly come from the user, provenance would pass.
  What then?
- **Pointer:** flip the fixture origins to `user`, re-run; read
  `gate.py:check_dataflow`.
- **Answer:** sensitive (`internal`/`pii-high`) data to an external recipient via a
  public egress tool is blocked pending approval. Revert the fixture after.

### Capstone — tool provenance
- **Nudge:** which server served the untrusted page, and how is it marked?
- **Pointer:** `mcp_servers` — the `web` server is `provenance="unverified"`.
- **Answer:** don't treat a tool description from an unverified server as guidance;
  log the origin of every instruction followed.

---

## Post-workshop

### Checklist for a real agent system
- [ ] You can list every channel the agent reads untrusted text from.
- [ ] Instructions are honoured only from the user; tool results / web / memory are
      data.
- [ ] Memory entries carry provenance; untrusted notes are never read back as
      commands.
- [ ] Sensitive data cannot reach an external egress tool without human approval.
- [ ] Tool descriptions from unverified/unpinned servers are not treated as
      guidance.
- [ ] Every action the agent takes is logged with the origin that prompted it.

### post-01 — structural beats semantic
Don't build a classifier to spot "malicious prompts." Decide by *origin* (who said
it) and *data class* (what's moving). Those don't depend on guessing intent and
don't degrade as phrasing changes.

### post-02 — the egress chokepoint
Most agent damage is data leaving or state changing. Put the tightest control on
the few egress/mutating tools, not on the many read tools.

### post-03 — pin and attribute your tools
An agent's tools come from servers. Pin versions, allowlist servers, and treat an
unverified server's descriptions as untrusted input — because that's what they are.
