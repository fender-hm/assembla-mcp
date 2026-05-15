import json
import pytest
from unittest.mock import MagicMock, patch
import assembla_mcp.state as state_module
from assembla_mcp.tools.components import list_components


@pytest.fixture(autouse=True)
def setup_state():
    state_module.state.active_space_id = "space-123"
    yield
    state_module.state.active_space_id = None


@pytest.fixture
def mock_client():
    with patch("assembla_mcp.tools.components.get_client") as m:
        c = MagicMock()
        m.return_value = c
        yield c


def test_list_components(mock_client):
    mock_client.get.return_value = [{"id": "c1", "name": "Backend"}]
    result = list_components()
    data = json.loads(result)
    assert data[0]["name"] == "Backend"
    mock_client.get.assert_called_once_with("/spaces/space-123/components")


def test_list_components_no_space():
    state_module.state.active_space_id = None
    assert "No active space" in list_components()


def test_list_components_error(mock_client):
    mock_client.get.return_value = {"error": "Not found (404)"}
    result = list_components()
    assert "Not found" in result