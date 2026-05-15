import json
import pytest
from unittest.mock import MagicMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.spaces import list_spaces, set_active_space


@pytest.fixture(autouse=True)
def reset_state():
    state_module.state.active_space_id = None
    state_module.state.spaces_cache = []
    yield
    state_module.state.active_space_id = None
    state_module.state.spaces_cache = []


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.spaces.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


def test_list_spaces_returns_json(mock_client):
    mock_client.get.return_value = [{"id": "abc", "name": "My Project"}]
    result = list_spaces()
    data = json.loads(result)
    assert data[0]["name"] == "My Project"


def test_list_spaces_caches_result(mock_client):
    mock_client.get.return_value = [{"id": "abc", "name": "My Project"}]
    list_spaces()
    assert state_module.state.spaces_cache == [{"id": "abc", "name": "My Project"}]


def test_list_spaces_error_propagated(mock_client):
    mock_client.get.return_value = {"error": "Forbidden (403) — check API key permissions"}
    result = list_spaces()
    assert "Forbidden" in result


def test_set_active_space_by_id(mock_client):
    state_module.state.spaces_cache = [{"id": "abc", "name": "My Project"}]
    result = set_active_space("abc")
    assert state_module.state.active_space_id == "abc"
    assert "My Project" in result


def test_set_active_space_by_name(mock_client):
    state_module.state.spaces_cache = [{"id": "abc", "name": "My Project"}]
    result = set_active_space("My Project")
    assert state_module.state.active_space_id == "abc"
    assert "My Project" in result


def test_set_active_space_fetches_if_cache_empty(mock_client):
    mock_client.get.return_value = [{"id": "xyz", "name": "Other"}]
    result = set_active_space("xyz")
    assert state_module.state.active_space_id == "xyz"


def test_set_active_space_not_found(mock_client):
    state_module.state.spaces_cache = [{"id": "abc", "name": "My Project"}]
    result = set_active_space("nonexistent")
    assert "not found" in result.lower()
    assert state_module.state.active_space_id is None