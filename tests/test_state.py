import pytest
import assembla_mcp.state as state_module


@pytest.fixture(autouse=True)
def reset_state():
    state_module.state.active_space_id = None
    state_module.state.spaces_cache = []
    yield
    state_module.state.active_space_id = None
    state_module.state.spaces_cache = []


def test_initial_state_is_none():
    assert state_module.state.active_space_id is None


def test_set_active_space():
    state_module.state.active_space_id = "abc123"
    assert state_module.state.active_space_id == "abc123"


def test_spaces_cache_starts_empty():
    assert state_module.state.spaces_cache == []


def test_spaces_cache_set():
    state_module.state.spaces_cache = [{"id": "x", "name": "My Space"}]
    assert len(state_module.state.spaces_cache) == 1