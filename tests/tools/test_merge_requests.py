import json
import pytest
from unittest.mock import MagicMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.merge_requests import (
    list_merge_requests, get_merge_request, create_merge_request,
    update_merge_request, approve_merge_request, ignore_merge_request,
    merge_merge_request, list_mr_comments, add_mr_comment,
)

BASE = "/spaces/space-123/space_tools/tool-456/merge_requests"


@pytest.fixture(autouse=True)
def setup_state():
    state_module.state.active_space_id = "space-123"
    state_module.state.active_tool_id = "tool-456"
    yield
    state_module.state.active_space_id = None
    state_module.state.active_tool_id = None


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.merge_requests.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


def test_list_merge_requests(mock_client):
    mock_client.get.return_value = [{"id": "mr1", "title": "Add feature"}]
    result = list_merge_requests()
    assert '"title": "Add feature"' in result
    mock_client.get.assert_called_once_with(BASE, params={"page": 1, "per_page": 25})


def test_list_merge_requests_status_filter(mock_client):
    mock_client.get.return_value = [{"id": "mr1", "status": "open"}]
    list_merge_requests(status="open")
    mock_client.get.assert_called_once_with(BASE, params={"page": 1, "per_page": 25, "status": "open"})


def test_list_merge_requests_no_space():
    state_module.state.active_space_id = None
    assert "No active space" in list_merge_requests()


def test_list_merge_requests_no_tool():
    state_module.state.active_tool_id = None
    assert "No active tool" in list_merge_requests()


def test_get_merge_request(mock_client):
    mock_client.get.return_value = {"id": "mr1", "title": "Fix"}
    result = get_merge_request("mr1")
    assert '"id": "mr1"' in result
    mock_client.get.assert_called_once_with(f"{BASE}/mr1")


def test_create_merge_request(mock_client):
    mock_client.post.return_value = {"id": "mr2", "title": "New MR"}
    result = create_merge_request("New MR", "feature-branch", "main")
    assert '"id": "mr2"' in result
    data = mock_client.post.call_args[0][1]["merge_request"]
    assert data["title"] == "New MR"
    assert data["source_symbol"] == "feature-branch"
    assert data["target_symbol"] == "main"


def test_create_merge_request_omits_source_cleanup_by_default(mock_client):
    mock_client.post.return_value = {"id": "mr2"}
    create_merge_request("New MR", "feature-branch", "main")
    data = mock_client.post.call_args[0][1]["merge_request"]
    assert "source_cleanup" not in data


def test_create_merge_request_source_cleanup(mock_client):
    mock_client.post.return_value = {"id": "mr2"}
    create_merge_request("New MR", "feature-branch", "main", source_cleanup=True)
    data = mock_client.post.call_args[0][1]["merge_request"]
    assert data["source_cleanup"] is True


def test_update_merge_request(mock_client):
    mock_client.put.return_value = {"id": "mr1", "title": "Updated"}
    result = update_merge_request("mr1", title="Updated")
    assert '"title": "Updated"' in result
    data = mock_client.put.call_args[0][1]["merge_request"]
    assert data["title"] == "Updated"


def test_update_merge_request_target_branch(mock_client):
    mock_client.put.return_value = {"id": "mr1"}
    update_merge_request("mr1", target_branch="develop")
    data = mock_client.put.call_args[0][1]["merge_request"]
    assert data["target_symbol"] == "develop"


def test_update_merge_request_source_cleanup(mock_client):
    mock_client.put.return_value = {"id": "mr1"}
    update_merge_request("mr1", source_cleanup=True)
    data = mock_client.put.call_args[0][1]["merge_request"]
    assert data["source_cleanup"] is True


def test_update_merge_request_source_cleanup_false(mock_client):
    mock_client.put.return_value = {"id": "mr1"}
    update_merge_request("mr1", source_cleanup=False)
    data = mock_client.put.call_args[0][1]["merge_request"]
    assert data["source_cleanup"] is False


def test_approve_merge_request_resolves_latest_version(mock_client):
    mock_client.get.return_value = [
        {"version": 1, "latest": False},
        {"version": 2, "latest": True},
    ]
    mock_client.post.return_value = [{"vote": 1}]
    result = approve_merge_request("mr1")
    assert '"vote": 1' in result
    mock_client.get.assert_called_once_with(f"{BASE}/mr1/versions")
    mock_client.post.assert_called_once_with(f"{BASE}/mr1/versions/2/votes/upvote", {})


def test_approve_merge_request_explicit_version(mock_client):
    mock_client.post.return_value = [{"vote": 1}]
    approve_merge_request("mr1", version=3)
    mock_client.get.assert_not_called()
    mock_client.post.assert_called_once_with(f"{BASE}/mr1/versions/3/votes/upvote", {})


def test_approve_merge_request_no_versions(mock_client):
    mock_client.get.return_value = []
    assert "no versions" in approve_merge_request("mr1").lower()
    mock_client.post.assert_not_called()


def test_ignore_merge_request(mock_client):
    mock_client.put.return_value = {"success": True}
    result = ignore_merge_request("mr1")
    assert "ignored" in result.lower()
    mock_client.put.assert_called_once_with(f"{BASE}/mr1/ignore")


def test_merge_merge_request(mock_client):
    mock_client.put.return_value = {"success": True}
    result = merge_merge_request("mr1")
    assert "merged" in result.lower()
    mock_client.put.assert_called_once_with(f"{BASE}/mr1/merge_and_close")


def test_ignore_merge_request_no_tool():
    state_module.state.active_tool_id = None
    assert "No active tool" in ignore_merge_request("mr1")


def test_list_mr_comments(mock_client):
    mock_client.get.return_value = [{"id": "c1", "body": "LGTM"}]
    result = list_mr_comments("mr1")
    assert '"body": "LGTM"' in result
    mock_client.get.assert_called_once_with(f"{BASE}/mr1/comments")


def test_add_mr_comment(mock_client):
    mock_client.post.return_value = {"id": "c2", "body": "Please fix tests"}
    result = add_mr_comment("mr1", "Please fix tests")
    assert '"body": "Please fix tests"' in result
    data = mock_client.post.call_args[0][1]["comment"]
    assert data["body"] == "Please fix tests"


def test_error_propagated(mock_client):
    mock_client.get.return_value = {"error": "Not found (404): no body"}
    result = get_merge_request("bad")
    assert "Not found" in result