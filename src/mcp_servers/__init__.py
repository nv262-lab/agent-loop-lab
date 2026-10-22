"""Three mock MCP servers for the lab.

These are NOT real Model Context Protocol servers. They are tiny Python
objects that imitate the one property that matters for the exercises: a
server advertises *tools*, and each tool has a human-readable *description*
that the model reads as guidance (slide 11: "most of what an agent reads,
nobody typed").

Everything is offline. The mail server never opens a socket; it appends to
a local outbox file so students can see what *would* have been sent. All
data is fictional and all keys are obvious placeholders.
"""
from __future__ import annotations

import json
from pathlib import Path

from .base import MockServer, Tool

ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "data"
OUTBOX = DATA / "outbox.txt"
WEB = DATA / "web_pages"


# --- files server -----------------------------------------------------------
# Internal data the agent can read. One file is labelled pii-high so the
# data-class gate (Exercise 4) has something to protect.

def _files_read(path: str = "") -> str:
    store = {
        "notes/roadmap.md": ("internal", "Q3 roadmap: ship the agent gateway."),
        "customers/pii.csv": ("pii-high", "name,email\nA. Example,a@example.com"),
        "readme.txt": ("public", "Welcome to the fixture file store."),
    }
    cls, body = store.get(path, ("public", f"(no such file: {path})"))
    # The returned text is tagged so the harness can track data class flow.
    return json.dumps({"path": path, "data_class": cls, "content": body})


def _files_list() -> str:
    return "notes/roadmap.md\ncustomers/pii.csv\nreadme.txt"


# --- mail server ------------------------------------------------------------
# Public egress. It NEVER sends; it appends to data/outbox.txt so learners can
# see what would have left. This is the sink the gate must protect.

def _mail_send(to: str = "", body: str = "") -> str:
    DATA.mkdir(parents=True, exist_ok=True)
    with OUTBOX.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"to": to, "body": body}) + "\n")
    return f"(simulated) queued mail to {to} — written to outbox, not sent"


# --- web server -------------------------------------------------------------
# Untrusted content from the open web. Returns a fixture page. One page carries
# a benign, clearly-labelled prompt-injection *specimen* so the lab can teach
# detection — the harness only treats it as instructions in the deliberately
# naive mode (Exercise 1), to demonstrate why that is wrong.

def _web_fetch(url: str = "") -> str:
    name = url.rstrip("/").split("/")[-1] or "index"
    page = WEB / f"{name}.json"
    if page.exists():
        return page.read_text(encoding="utf-8")
    return json.dumps({"url": url, "data_class": "public",
                       "content": "(page not found)"})


def build_servers() -> dict[str, MockServer]:
    files = MockServer("files", provenance="pinned")
    files.register(Tool("files.read", "Read an internal file by path.",
                        _files_read, data_class="internal"))
    files.register(Tool("files.list", "List available files.",
                        _files_list, data_class="internal"))

    mail = MockServer("mail", provenance="pinned")
    mail.register(Tool("mail.send", "Send an email to a recipient.",
                       _mail_send, data_class="public"))

    # NOTE: this server is 'unverified' — not version-pinned/allowlisted
    # (slide 18, missing sensors). Its tool description is attacker-controllable.
    web = MockServer("web", provenance="unverified")
    web.register(Tool(
        "web.fetch",
        # The description itself is an untrusted input channel. In this lab it is
        # benign; the point is that nobody on your team typed it.
        "Fetch a web page and return its text.",
        _web_fetch, data_class="public"))

    return {"files": files, "mail": mail, "web": web}
