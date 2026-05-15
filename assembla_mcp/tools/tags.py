from __future__ import annotations
import json
from typing import Optional
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


def list_ticket_tags(ticket_number: int, space_id: Optional[str] = None) -> str:
    """List all tags on a ticket."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/tickets/{ticket_number}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    tags_str = result.get("tags") or ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    return json.dumps(tags, indent=2)


def add_ticket_tag(ticket_number: int, tag: str, space_id: Optional[str] = None) -> str:
    """Add a tag to a ticket."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/tickets/{ticket_number}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    tags_str = result.get("tags") or ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    if tag in tags:
        return f"Tag '{tag}' already present on ticket #{ticket_number}."
    tags.append(tag)
    updated = get_client().put(
        f"/spaces/{sid}/tickets/{ticket_number}",
        {"ticket": {"tags": ",".join(tags)}},
    )
    if isinstance(updated, dict) and "error" in updated:
        return updated["error"]
    return f"Tag '{tag}' added to ticket #{ticket_number}. Tags: {','.join(tags)}"


def remove_ticket_tag(ticket_number: int, tag: str, space_id: Optional[str] = None) -> str:
    """Remove a tag from a ticket."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/tickets/{ticket_number}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    tags_str = result.get("tags") or ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    if tag not in tags:
        return f"Tag '{tag}' not found on ticket #{ticket_number}."
    tags.remove(tag)
    updated = get_client().put(
        f"/spaces/{sid}/tickets/{ticket_number}",
        {"ticket": {"tags": ",".join(tags)}},
    )
    if isinstance(updated, dict) and "error" in updated:
        return updated["error"]
    return f"Tag '{tag}' removed from ticket #{ticket_number}."


def register(mcp) -> None:
    for fn in [list_ticket_tags, add_ticket_tag, remove_ticket_tag]:
        mcp.tool()(fn)