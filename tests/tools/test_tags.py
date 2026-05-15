import json
import pytest
from unittest.mock import MagicMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.tags import list_ticket_tags, add_ticket_tag, remove_ticket_tag


@pytest.fixture(autouse=True)
def setup_state():
    state_module.state.active_space_id = "space-123"
    yield
    state_module.state.active_space_id = None


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.tags.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


def test_list_ticket_tags(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": "urgent,backend"}
    result = list_ticket_tags(1)
    data = json.loads(result)
    assert "urgent" in data
    assert "backend" in data


def test_list_ticket_tags_empty(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": ""}
    result = list_ticket_tags(1)
    assert json.loads(result) == []


def test_list_ticket_tags_no_space():
    state_module.state.active_space_id = None
    assert "No active space" in list_ticket_tags(1)


def test_add_ticket_tag(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": "urgent"}
    mock_client.put.return_value = {"number": 1, "tags": "urgent,backend"}
    result = add_ticket_tag(1, "backend")
    assert "backend" in result
    put_data = mock_client.put.call_args[0][1]["ticket"]
    assert "urgent" in put_data["tags"]
    assert "backend" in put_data["tags"]


def test_add_ticket_tag_already_present(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": "urgent,backend"}
    result = add_ticket_tag(1, "urgent")
    assert "already" in result.lower()
    mock_client.put.assert_not_called()


def test_remove_ticket_tag(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": "urgent,backend"}
    mock_client.put.return_value = {"number": 1, "tags": "backend"}
    result = remove_ticket_tag(1, "urgent")
    assert "removed" in result.lower()
    put_data = mock_client.put.call_args[0][1]["ticket"]
    assert "urgent" not in put_data["tags"]


def test_remove_ticket_tag_not_present(mock_client):
    mock_client.get.return_value = {"number": 1, "tags": "backend"}
    result = remove_ticket_tag(1, "urgent")
    assert "not found" in result.lower()
    mock_client.put.assert_not_called()