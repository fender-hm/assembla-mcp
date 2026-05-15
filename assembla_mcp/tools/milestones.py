from __future__ import annotations
import json
from typing import Optional
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


def list_milestones(space_id: Optional[str] = None) -> str:
    """List all milestones in the active space."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/milestones")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def get_milestone(milestone_id: str, space_id: Optional[str] = None) -> str:
    """Get a milestone by its ID."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/milestones/{milestone_id}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def create_milestone(
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    space_id: Optional[str] = None,
) -> str:
    """Create a milestone. due_date format: YYYY-MM-DD."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    milestone: dict = {"title": title, "description": description}
    if due_date:
        milestone["due_date"] = due_date
    result = get_client().post(f"/spaces/{sid}/milestones", {"milestone": milestone})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def update_milestone(
    milestone_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    space_id: Optional[str] = None,
) -> str:
    """Update a milestone's fields."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    milestone: dict = {}
    if title is not None:
        milestone["title"] = title
    if description is not None:
        milestone["description"] = description
    if due_date is not None:
        milestone["due_date"] = due_date
    result = get_client().put(f"/spaces/{sid}/milestones/{milestone_id}", {"milestone": milestone})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def delete_milestone(milestone_id: str, space_id: Optional[str] = None) -> str:
    """Delete a milestone by its ID."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().delete(f"/spaces/{sid}/milestones/{milestone_id}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Milestone {milestone_id} deleted successfully."


def register(mcp) -> None:
    for fn in [list_milestones, get_milestone, create_milestone, update_milestone, delete_milestone]:
        mcp.tool()(fn)