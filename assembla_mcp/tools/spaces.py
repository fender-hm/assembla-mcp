from __future__ import annotations
import json
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def list_spaces() -> str:
    """List all Assembla spaces accessible with the current API key."""
    result = get_client().get("/spaces")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    spaces = result if isinstance(result, list) else []
    state.spaces_cache = spaces
    return json.dumps(spaces, indent=2)


def set_active_space(space_id_or_name: str) -> str:
    """Set the active space for this session by space ID or name. All subsequent tools use this space by default."""
    if not state.spaces_cache:
        result = get_client().get("/spaces")
        if isinstance(result, dict) and "error" in result:
            return result["error"]
        state.spaces_cache = result if isinstance(result, list) else []

    match = None
    for s in state.spaces_cache:
        if s.get("id") == space_id_or_name or s.get("name") == space_id_or_name:
            match = s
            break

    if not match:
        return f"Space '{space_id_or_name}' not found. Call list_spaces to see available spaces."

    state.active_space_id = match["id"]
    return f"Active space set to '{match['name']}' (id: {match['id']})"


def register(mcp) -> None:
    mcp.tool()(list_spaces)
    mcp.tool()(set_active_space)