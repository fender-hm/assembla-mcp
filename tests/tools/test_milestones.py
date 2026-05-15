import json
import pytest
from unittest.mock import MagicMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.milestones import (
    list_milestones, get_milestone, create_milestone, update_milestone, delete_milestone
)


@pytest.fixture(autouse=True)
def setup_state():
    state_module.state.active_space_id = "space-123"
    yield
    state_module.state.active_space_id = None


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.milestones.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


def test_list_milestones(mock_client):
    mock_client.get.return_value = [{"id": "m1", "title": "v1.0"}]
    result = list_milestones()
    assert '"title": "v1.0"' in result
    mock_client.get.assert_called_once_with("/spaces/space-123/milestones")


def test_list_milestones_no_space():
    state_module.state.active_space_id = None
    assert "No active space" in list_milestones()


def test_get_milestone(mock_client):
    mock_client.get.return_value = {"id": "m1", "title": "v1.0"}
    result = get_milestone("m1")
    assert '"id": "m1"' in result
    mock_client.get.assert_called_once_with("/spaces/space-123/milestones/m1")


def test_create_milestone(mock_client):
    mock_client.post.return_value = {"id": "m2", "title": "v2.0"}
    result = create_milestone("v2.0")
    assert '"id": "m2"' in result
    data = mock_client.post.call_args[0][1]["milestone"]
    assert data["title"] == "v2.0"


def test_create_milestone_with_due_date(mock_client):
    mock_client.post.return_value = {"id": "m3", "title": "Sprint 1", "due_date": "2026-06-01"}
    create_milestone("Sprint 1", due_date="2026-06-01")
    data = mock_client.post.call_args[0][1]["milestone"]
    assert data["due_date"] == "2026-06-01"


def test_update_milestone(mock_client):
    mock_client.put.return_value = {"id": "m1", "title": "v1.1"}
    result = update_milestone("m1", title="v1.1")
    assert '"title": "v1.1"' in result
    data = mock_client.put.call_args[0][1]["milestone"]
    assert data["title"] == "v1.1"


def test_delete_milestone(mock_client):
    mock_client.delete.return_value = {"success": True}
    result = delete_milestone("m1")
    assert "deleted" in result
    mock_client.delete.assert_called_once_with("/spaces/space-123/milestones/m1")


def test_error_propagated(mock_client):
    mock_client.get.return_value = {"error": "Not found (404)"}
    result = get_milestone("bad")
    assert "Not found" in result