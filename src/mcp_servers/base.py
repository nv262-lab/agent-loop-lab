"""Shared types for the mock MCP servers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class Tool:
    name: str
    description: str                 # model-visible text — an untrusted input channel
    handler: Callable[..., str]
    data_class: str = "public"       # public | internal | pii-high — used by the gate


class MockServer:
    """A named bundle of tools, the way an MCP client would see one server."""

    def __init__(self, name: str, provenance: str = "pinned"):
        self.name = name
        # provenance imitates slide 18 "missing sensors": where did this server
        # come from? "pinned" = version-pinned + allowlisted; "unverified" = not.
        self.provenance = provenance
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def call(self, name: str, **kwargs) -> str:
        if name not in self._tools:
            raise KeyError(f"{self.name}: no such tool {name!r}")
        return self._tools[name].handler(**kwargs)
