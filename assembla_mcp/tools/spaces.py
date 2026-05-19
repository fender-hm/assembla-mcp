from __future__ import annotations
import json
from typing import Optional
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


def list_space_tools(space_id: Optional[str] = None) -> str:
    """List all tools (git repos, SVN, etc.) configured for the active space."""
    sid = space_id or state.active_space_id
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/space_tools")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    tools = result if isinstance(result, list) else []
    state.tools_cache = tools
    return json.dumps(tools, indent=2)


def set_active_tool(tool_id: str, space_id: Optional[str] = None) -> str:
    """Set the active space tool (e.g. a git repo) by its ID. Required before using merge request tools."""
    sid = space_id or state.active_space_id
    if not sid:
        return "No active space. Call set_active_space first."
    if not state.tools_cache:
        result = get_client().get(f"/spaces/{sid}/space_tools")
        if isinstance(result, dict) and "error" in result:
            return result["error"]
        state.tools_cache = result if isinstance(result, list) else []

    match = next((t for t in state.tools_cache if t.get("id") == tool_id), None)
    if not match:
        return f"Tool '{tool_id}' not found. Call list_space_tools to see available tools."
    state.active_tool_id = match["id"]
    return f"Active tool set to '{match.get('name', tool_id)}' (id: {match['id']})"


def register(mcp) -> None:
    mcp.tool()(list_spaces)
    mcp.tool()(set_active_space)
    mcp.tool()(list_space_tools)
    mcp.tool()(set_active_tool)