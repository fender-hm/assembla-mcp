from __future__ import annotations
from typing import Optional


class State:
    def __init__(self) -> None:
        self.active_space_id: Optional[str] = None
        self.spaces_cache: list[dict] = []
        self.active_tool_id: Optional[str] = None
        self.tools_cache: list[dict] = []


state = State()