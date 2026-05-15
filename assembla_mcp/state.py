from __future__ import annotations
from typing import Optional


class State:
    def __init__(self) -> None:
        self.active_space_id: Optional[str] = None
        self.spaces_cache: list[dict] = []


state = State()