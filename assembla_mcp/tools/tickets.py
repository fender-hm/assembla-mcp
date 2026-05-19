# assembla_mcp/tools/tickets.py
from __future__ import annotations
import json
from typing import Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context
from mcp.server.elicitation import AcceptedElicitation
from assembla_mcp.client import get_client
from assembla_mcp.state import state


class _PriorityInput(BaseModel):
    priority: int = Field(
        description="1 = Highest, 2 = High, 3 = Medium, 4 = Low, 5 = Lowest",
        ge=1,
        le=5,
    )


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


async def list_tickets(
    ctx: Context,
    space_id: Optional[str] = None,
    status: Optional[str] = None,
    milestone_id: Optional[str] = None,
    component_id: Optional[str] = None,
    tag: Optional[str] = None,
    priority: Optional[int] = None,
    page: int = 1,
    per_page: int = 25,
) -> str:
    """List tickets in the active space. Filter by status, milestone_id, component_id, tag, or priority (1=highest, 5=lowest)."""
    if priority is None:
        elicit_result = await ctx.elicit(
            message="Filter by priority? Enter 1 (Highest), 2 (High), 3 (Medium), 4 (Low), or 5 (Lowest). Cancel to list all.",
            schema=_PriorityInput,
        )
        if isinstance(elicit_result, AcceptedElicitation):
            priority = elicit_result.data.priority

    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    params: dict = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    if milestone_id:
        params["milestone_id"] = milestone_id
    result = get_client().get(f"/spaces/{sid}/tickets", params=params)
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    tickets = result if isinstance(result, list) else result.get("tickets", [])
    if component_id:
        tickets = [t for t in tickets if str(t.get("component_id", "")) == component_id]
    if tag:
        tickets = [t for t in tickets if tag in (t.get("tags") or "")]
    if priority is not None:
        tickets = [t for t in tickets if t.get("priority") == priority]
    return json.dumps(tickets, indent=2)


def get_ticket(number: int, space_id: Optional[str] = None) -> str:
    """Get a single ticket by its number."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/tickets/{number}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def create_ticket(
    summary: str,
    description: str = "",
    status: str = "new",
    priority: int = 3,
    milestone_id: Optional[str] = None,
    assigned_to_id: Optional[str] = None,
    component_id: Optional[str] = None,
    tags: Optional[str] = None,
    space_id: Optional[str] = None,
) -> str:
    """Create a new ticket in the active space."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    ticket: dict = {"summary": summary, "description": description, "status": status, "priority": priority}
    if milestone_id:
        ticket["milestone_id"] = milestone_id
    if assigned_to_id:
        ticket["assigned_to_id"] = assigned_to_id
    if component_id:
        ticket["component_id"] = component_id
    if tags:
        ticket["tags"] = tags
    result = get_client().post(f"/spaces/{sid}/tickets", {"ticket": ticket})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def update_ticket(
    number: int,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    milestone_id: Optional[str] = None,
    assigned_to_id: Optional[str] = None,
    component_id: Optional[str] = None,
    tags: Optional[str] = None,
    space_id: Optional[str] = None,
) -> str:
    """Update fields on an existing ticket."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    ticket: dict = {}
    if summary is not None:
        ticket["summary"] = summary
    if description is not None:
        ticket["description"] = description
    if status is not None:
        ticket["status"] = status
    if priority is not None:
        ticket["priority"] = priority
    if milestone_id is not None:
        ticket["milestone_id"] = milestone_id
    if assigned_to_id is not None:
        ticket["assigned_to_id"] = assigned_to_id
    if component_id is not None:
        ticket["component_id"] = component_id
    if tags is not None:
        ticket["tags"] = tags
    result = get_client().put(f"/spaces/{sid}/tickets/{number}", {"ticket": ticket})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def delete_ticket(number: int, space_id: Optional[str] = None) -> str:
    """Delete a ticket by its number."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().delete(f"/spaces/{sid}/tickets/{number}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Ticket #{number} deleted successfully."


def register(mcp) -> None:
    for fn in [list_tickets, get_ticket, create_ticket, update_ticket, delete_ticket]:
        mcp.tool()(fn)