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
    source_cleanup: bool = False,
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """Create a new merge request.

    source_branch / target_branch: branch, tag, or revision names. These are sent
    to Assembla as source_symbol / target_symbol.

    source_cleanup: delete the source branch once the merge request is merged or
    ignored ("Delete branch after merge request is merged or ignored" in the web
    UI). Omitted from the payload when False, so Assembla applies its own default.

    Note: squashing commits on merge has no API field — it is a repository
    setting ("Squash commits on merge default enabled") or a per-request checkbox
    in the web UI.
    """
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    mr: dict = {
        "title": title,
        "source_symbol": source_branch,
        "target_symbol": target_branch,
        "description": description,
    }
    if source_cleanup:
        mr["source_cleanup"] = True
    data = {"merge_request": mr}
    result = get_client().post(_mr_base(sid, tid), data)
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def update_merge_request(
    mr_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    target_branch: Optional[str] = None,
    source_cleanup: Optional[bool] = None,
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """Update a merge request's title, description, target branch, or source cleanup.

    source_cleanup: delete the source branch once the merge request is merged or
    ignored. Pass True/False to change it; leave unset to keep the current value.
    """
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
    if source_cleanup is not None:
        mr["source_cleanup"] = source_cleanup
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}", {"merge_request": mr})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def approve_merge_request(
    mr_id: str,
    version: Optional[int] = None,
    space_id: Optional[str] = None,
    tool_id: Optional[str] = None,
) -> str:
    """Approve a merge request by upvoting one of its versions.

    Assembla has no "approve" endpoint — review approval is a vote on a specific
    merge request version. Leave version unset to upvote the latest one.
    """
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    base = _mr_base(sid, tid)
    if version is None:
        versions = get_client().get(f"{base}/{mr_id}/versions")
        if isinstance(versions, dict) and "error" in versions:
            return versions["error"]
        if not versions:
            return f"Merge request {mr_id} has no versions to approve."
        latest = next((v for v in versions if v.get("latest")), versions[-1])
        version = latest["version"]
    result = get_client().post(f"{base}/{mr_id}/versions/{version}/votes/upvote", {})
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return json.dumps(result, indent=2)


def ignore_merge_request(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Ignore (reject) a merge request without merging it.

    This is Assembla's term for declining — the merge request ends up with the
    "ignored" status. If it was created with source_cleanup, the source branch is
    deleted at this point.
    """
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}/ignore")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} ignored."


def merge_merge_request(mr_id: str, space_id: Optional[str] = None, tool_id: Optional[str] = None) -> str:
    """Apply and close a merge request (merge it into the target branch)."""
    sid = _resolve_space(space_id)
    if not sid:
        return "No active space. Call set_active_space first."
    tid = _resolve_tool(tool_id)
    if not tid:
        return "No active tool. Call list_space_tools then set_active_tool with the git repo tool ID."
    result = get_client().put(f"{_mr_base(sid, tid)}/{mr_id}/merge_and_close")
    if isinstance(result, dict) and "error" in result:
        return result["error"]
    return f"Merge request {mr_id} merged and closed."


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
        update_merge_request, approve_merge_request, ignore_merge_request,
        merge_merge_request, list_mr_comments, add_mr_comment,
    ]:
        mcp.tool()(fn)