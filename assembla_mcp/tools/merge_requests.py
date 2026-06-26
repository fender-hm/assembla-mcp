from __future__ import annotations
import json
from typing import Optional
from assembla_mcp.client import get_client
from assembla_mcp.state import state


def _resolve_space(space_id: Optional[str]) -> Optional[str]:
    return space_id or state.active_space_id


def _resolve_tool(tool_id: Optional[str]) -> Optional[str]:
    return tool_id or state.active_tool_id


def _mr_base(sid: str, tid: str) -> str:
    return f"/spaces/{sid}/space_tools/{tid}/merge_requests"


def list_merge_requests(
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 25,
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """List merge requests for the active space tool (git repo). Call list_space_tools then set_active_tool first.

    status: filter by status — 'open', 'closed', or 'ignored' (default: all).
    """
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    params: dict = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    result = get_client().get(_mr_base(sid, tid), params=params)
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def get_merge_request(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Get a single merge request by its ID."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().get(f"{_mr_base(sid, tid)}/{mr_id}")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def create_merge_request(
    title: str,
    source_branch: str,
    target_branch: str,
    description: str = "",
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """Create a new merge request.

    source_branch / target_branch: branch, tag, or revision names. These are sent
    to Assembla as source_symbol / target_symbol.
    """
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    data = {
        "merge_request": {
            "title": title,
            "source_symbol": source_branch,
            "target_symbol": target_branch,
            "description": description,
        }
    }
    result = get_client().post(_mr_base(sid, tid), data)
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def update_merge_request(
    mr_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    target_branch: Optional[str] = None,
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """Update a merge request's title, description, or target branch."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    mr: dict = {}
    if title is not None:
        mr["title"] = title
    if description is not None:
        mr["description"] = description
    if target_branch is not None:
        mr["target_symbol"] = target_branch
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}", {"merge_request": mr})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def approve_merge_request(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Approve a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}/approve")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} approved."


def decline_merge_request(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Decline a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}/decline")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} declined."


def list_mr_comments(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """List all comments on a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().get(f"{_mr_base(sid, tid)}/{mr_id}/comments")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def add_mr_comment(mr_id: str, body: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Add a comment to a merge request."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().post(
        f"{_mr_base(sid, tid)}/{mr_id}/comments",
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