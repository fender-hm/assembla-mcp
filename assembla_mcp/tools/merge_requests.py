from __future__ import annotations
import json
from typing import Optional
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


def list_merge_requests(space_id: Optional[str] = None) -> str:
    """List all merge requests in the active space."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/merge_requests")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def get_merge_request(mr_id: str, space_id: Optional[str] = None) -> str:
    """Get a single merge request by its ID."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/merge_requests/{mr_id}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def create_merge_request(
    title: str,
    source_branch: str,
    target_branch: str,
    description: str = "",
    space_id: Optional[str] = None,
) -> str:
    """Create a new merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    data = {
        "merge_request": {
            "title": title,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "description": description,
        }
    }
    result = get_client().post(f"/spaces/{sid}/merge_requests", data)
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def update_merge_request(
    mr_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    target_branch: Optional[str] = None,
    space_id: Optional[str] = None,
) -> str:
    """Update a merge request's title, description, or target branch."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    mr: dict = {}
    if title is not None:
        mr["title"] = title
    if description is not None:
        mr["description"] = description
    if target_branch is not None:
        mr["target_branch"] = target_branch
    result = get_client().put(f"/spaces/{sid}/merge_requests/{mr_id}", {"merge_request": mr})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def approve_merge_request(mr_id: str, space_id: Optional[str] = None) -> str:
    """Approve a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().put(f"/spaces/{sid}/merge_requests/{mr_id}/approve")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} approved."


def decline_merge_request(mr_id: str, space_id: Optional[str] = None) -> str:
    """Decline a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().put(f"/spaces/{sid}/merge_requests/{mr_id}/decline")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} declined."


def list_mr_comments(mr_id: str, space_id: Optional[str] = None) -> str:
    """List all comments on a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().get(f"/spaces/{sid}/merge_requests/{mr_id}/comments")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def add_mr_comment(mr_id: str, body: str, space_id: Optional[str] = None) -> str:
    """Add a comment to a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    result = get_client().post(
        f"/spaces/{sid}/merge_requests/{mr_id}/comments",
        {"comment": {"body": body}},
    )
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def register(mcp) -> None:
    for fn in [
        list_merge_requests, get_merge_request, create_merge_request,
        update_merge_request, approve_merge_request, decline_merge_request,
        list_mr_comments, add_mr_comment,
    ]:
        mcp.tool()(fn)