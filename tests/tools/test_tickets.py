# tests/tools/test_tickets.py
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.tickets import (
    list_tickets, get_ticket, create_ticket, update_ticket, delete_ticket, add_ticket_comment
)


@pytest.fixture(autouse=True)
def setup_state():
    state_module.state.active_space_id = "space-123"
    yield
    state_module.state.active_space_id = None


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.tickets.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.elicit = AsyncMock(return_value=MagicMock(spec=[]))  # not AcceptedElicitation → no priority filter
    return ctx


@pytest.mark.anyio
async def test_list_tickets_returns_json(mock_client, mock_ctx):
    mock_client.get.return_value = [{"number": 1, "summary": "Bug"}]
    result = await list_tickets(mock_ctx)
    data = json.loads(result)
    assert data[0]["number"] == 1
    mock_client.get.assert_called_once_with(
        "/spaces/space-123/tickets", params={"page": 1, "per_page": 25}
    )


@pytest.mark.anyio
async def test_list_tickets_no_active_space(mock_ctx):
    state_module.state.active_space_id = None
    result = await list_tickets(mock_ctx)
    assert "No active space" in result


@pytest.mark.anyio
async def test_list_tickets_with_status_filter(mock_client, mock_ctx):
    mock_client.get.return_value = [{"number": 1, "status": "open"}]
    await list_tickets(mock_ctx, status="open")
    mock_client.get.assert_called_once_with(
        "/spaces/space-123/tickets", params={"page": 1, "per_page": 25, "status": "open"}
    )


@pytest.mark.anyio
async def test_list_tickets_filters_by_component_client_side(mock_client, mock_ctx):
    mock_client.get.return_value = [
        {"number": 1, "component_id": "comp-1"},
        {"number": 2, "component_id": "comp-2"},
    ]
    result = await list_tickets(mock_ctx, component_id="comp-1")
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["number"] == 1


@pytest.mark.anyio
async def test_list_tickets_filters_by_tag_client_side(mock_client, mock_ctx):
    mock_client.get.return_value = [
        {"number": 1, "tags": "urgent,backend"},
        {"number": 2, "tags": "frontend"},
    ]
    result = await list_tickets(mock_ctx, tag="urgent")
    data = json.loads(result)
    assert len(data) == 1


def test_get_ticket(mock_client):
    mock_client.get.return_value = {"number": 42, "summary": "Fix it"}
    result = get_ticket(42)
    assert '"number": 42' in result
    mock_client.get.assert_called_once_with("/spaces/space-123/tickets/42")


def test_get_ticket_no_active_space():
    state_module.state.active_space_id = None
    result = get_ticket(1)
    assert "No active space" in result


def test_create_ticket(mock_client):
    mock_client.post.return_value = {"number": 5, "summary": "New"}
    result = create_ticket("New")
    assert '"number": 5' in result
    call_args = mock_client.post.call_args
    assert call_args[0][0] == "/spaces/space-123/tickets"
    assert call_args[0][1]["ticket"]["summary"] == "New"


def test_create_ticket_with_optional_fields(mock_client):
    mock_client.post.return_value = {"number": 6, "summary": "New"}
    create_ticket("New", milestone_id="m1", tags="urgent")
    data = mock_client.post.call_args[0][1]["ticket"]
    assert data["milestone_id"] == "m1"
    assert data["tags"] == "urgent"


def test_update_ticket(mock_client):
    mock_client.put.return_value = {"number": 1, "status": "closed"}
    result = update_ticket(1, status="closed")
    assert '"status": "closed"' in result
    call_args = mock_client.put.call_args
    assert call_args[0][1]["ticket"]["status"] == "closed"


def test_update_ticket_only_sends_provided_fields(mock_client):
    mock_client.put.return_value = {"number": 1}
    update_ticket(1, summary="Updated")
    data = mock_client.put.call_args[0][1]["ticket"]
    assert "summary" in data
    assert "status" not in data


def test_delete_ticket(mock_client):
    mock_client.delete.return_value = {"success": True}
    result = delete_ticket(1)
    assert "deleted" in result
    mock_client.delete.assert_called_once_with("/spaces/space-123/tickets/1")


def test_error_propagated(mock_client):
    mock_client.get.return_value = {"error": "Not found (404)"}
    result = get_ticket(999)
    assert "Not found" in result


def test_add_ticket_comment(mock_client):
    mock_client.post.return_value = {"id": "c1", "comment": "Looks good"}
    result = add_ticket_comment(42, "Looks good")
    assert '"comment": "Looks good"' in result
    mock_client.post.assert_called_once_with(
        "/spaces/space-123/tickets/42/ticket_comments",
        {"ticket_comment": {"comment": "Looks good"}},
    )


def test_add_ticket_comment_no_active_space():
    state_module.state.active_space_id = None
    result = add_ticket_comment(1, "Hi")
    assert "No active space" in result


def test_add_ticket_comment_error_propagated(mock_client):
    mock_client.post.return_value = {"error": "Forbidden (403)"}
    result = add_ticket_comment(1, "Hi")
    assert "Forbidden" in result