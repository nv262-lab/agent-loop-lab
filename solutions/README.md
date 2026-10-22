# Solutions

Reference answers. Try the exercises before reading.

## Exercise 1
The directives live in `data/web_pages/support_article.json` under `directives`,
with `origin: web`. Naive mode executes any directive it finds, so it reads
`customers/pii.csv` (pii-high) and emails it to `harvester@example.net`. Root
failure, one sentence: **the agent treated untrusted content as instructions.**

## Exercise 2
```bash
cd src && python3 -c "import sys;sys.path.insert(0,'.');from memory import Memory;print(Memory().recall('user@example.com'))"
```
The note has `origin='web', trusted=False`. Risk: it persists to
`data/memory_store.json` and is read back in later runs as context — tampered
memory outlives the session. The field that saves you is `origin`.

## Exercise 3
`gate.py:check_provenance` honours a directive only if `origin in {"user"}`.
Defended mode therefore rejects both web directives with `provenance_block`, while
the legitimate "email summary to user@example.com" still succeeds.

## Exercise 4
With origins flipped to `user`, provenance passes, and `gate.py:check_dataflow`
blocks `pii-high` data to the external `harvester@example.net`
(`dataflow_block`). Public data to the internal `user@example.com` is still
allowed. You want both controls: provenance stops untrusted *instructions*;
data-class control stops sensitive *data* leaving even on a user-origin request.

## Capstone — tool provenance (reference)

Add to `gate.py`:

```python
def check_tool_provenance(server_provenance: str) -> Verdict:
    """A tool description is guidance only if its server is verified/pinned."""
    if server_provenance == "pinned":
        return Verdict(True, "tool from a pinned/allowlisted server", "info")
    return Verdict(False,
                   f"tool description from '{server_provenance}' server treated as "
                   f"untrusted data, not guidance", "high")
```

Wire it in `agent.py` wherever a tool's `description` would influence behaviour:
call `check_tool_provenance(server.provenance)` and, on deny, log a
`tool_provenance_block` signal and ignore the description. The `web` server is
`unverified`, so its description is demoted from guidance to data — closing the
"missing sensor": you now know the origin of every instruction the agent acted on.
