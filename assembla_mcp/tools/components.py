from __future__ import annotations
import json
from typing import Optional
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


def list_components(space_id: Optional[str] = None) -> str:
    """List all components in the active space (read-only). Use component IDs when filtering or assigning tickets."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/components")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def register(mcp) -> None:
    mcp.tool()(list_components)