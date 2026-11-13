import pytest
import httpx
from unittest.mock import MagicMock, patch
from assembla_mcp.client import AssemblaClient, init_client, get_client, strip_astral
import assembla_mcp.client as client_module


@pytest.fixture(autouse=True)
def reset_client():
    client_module._instance = None
    yield
    client_module._instance = None


def _make_response(status_code: int, json_data=None, text=""):
    r = MagicMock(spec=httpx.Response)
    r.status_code = status_code
    r.json.return_value = json_data or {}
    r.text = text
    r.content = b"x" if json_data is not None else b""
    return r


def test_get_returns_json():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "get", return_value=_make_response(200, [{"id": "1"}])):
        result = c.get("/spaces")
    assert result == [{"id": "1"}]


def test_get_404_returns_error():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "get", return_value=_make_response(404)):
        result = c.get("/spaces/bad")
    assert result["error"].startswith("Not found (404)")


def test_get_403_returns_error():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "get", return_value=_make_response(403)):
        result = c.get("/spaces/private")
    assert result["error"].startswith("Forbidden (403)")


def test_get_500_returns_error():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "get", return_value=_make_response(500)):
        result = c.get("/spaces")
    assert "server error" in result["error"]


def test_get_timeout_returns_error():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "get", side_effect=httpx.TimeoutException("timeout")):
        result = c.get("/spaces")
    assert "timed out" in result["error"]


def test_delete_204_returns_success():
    c = AssemblaClient("key", "secret")
    r = MagicMock(spec=httpx.Response)
    r.status_code = 204
    with patch.object(c._http, "delete", return_value=r):
        result = c.delete("/spaces/x/tickets/1")
    assert result == {"success": True}


def test_init_and_get_client():
    init_client("k", "s")
    c = get_client()
    assert isinstance(c, AssemblaClient)


def test_get_client_before_init_raises():
    with pytest.raises(RuntimeError, match="not initialized"):
        get_client()

def test_strip_astral_removes_emoji_keeps_bmp_text():
    assert strip_astral("### 🔴 Blocker ✅ — Привет") == "###  Blocker ✅ — Привет"
    assert strip_astral("dev 👨‍💻 done") == "dev  done"
    assert strip_astral("ok 👍️!") == "ok !"


def test_strip_astral_walks_nested_payload():
    payload = {"comment": {"content": "a🟢b", "tags": ["x🔥", 3, None]}}
    assert strip_astral(payload) == {"comment": {"content": "ab", "tags": ["x", 3, None]}}


def test_post_sends_payload_without_emoji():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "post", return_value=_make_response(201, {"id": 1})) as post:
        c.post("/x", {"comment": {"content": "fix 🐛 now"}})
    assert post.call_args.kwargs["json"] == {"comment": {"content": "fix  now"}}


def test_put_sends_payload_without_emoji():
    c = AssemblaClient("key", "secret")
    with patch.object(c._http, "put", return_value=_make_response(200, {"id": 1})) as put:
        c.put("/x", {"ticket": {"summary": "🚀 release"}})
    assert put.call_args.kwargs["json"] == {"ticket": {"summary": " release"}}
