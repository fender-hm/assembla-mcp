from __future__ import annotations
import atexit
import re
import httpx
from typing import Any, Optional

_instance: Optional["AssemblaClient"] = None

# Assembla stores text as 3-byte UTF-8 and answers 500 to any 4-byte character (emoji
# like U+1F534). Drop them, with the variation selectors / joiners that trail them.
_ASTRAL_RE = re.compile("[\U00010000-\U0010FFFF][\uFE0F\u200D]*")


def strip_astral(value: Any) -> Any:
    """Remove 4-byte UTF-8 characters from every string in a JSON-like payload."""
    if isinstance(value, str):
        return _ASTRAL_RE.sub("", value)
    if isinstance(value, dict):
        return {k: strip_astral(v) for k, v in value.items()}
    if isinstance(value, list):
        return [strip_astral(v) for v in value]
    return value


class AssemblaClient:
    BASE_URL = "https://api.assembla.com/v1"

    def __init__(self, api_key: str, api_secret: str) -> None:
        self._headers = {
            "X-Api-Key": api_key,
            "X-Api-Secret": api_secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._http = httpx.Client(timeout=30.0)

    def get(self, path: str, params: dict | None = None) -> dict | list:
        try:
            r = self._http.get(f"{self.BASE_URL}{path}", headers=self._headers, params=params)
            return self._handle(r)
        except httpx.TimeoutException:
            return {"error": "Request timed out — check your connection"}
        except httpx.HTTPError as e:
            return {"error": f"Network error: {e}"}

    def post(self, path: str, data: dict) -> dict | list:
        try:
            r = self._http.post(f"{self.BASE_URL}{path}", headers=self._headers, json=strip_astral(data))
            return self._handle(r)
        except httpx.TimeoutException:
            return {"error": "Request timed out — check your connection"}
        except httpx.HTTPError as e:
            return {"error": f"Network error: {e}"}

    def put(self, path: str, data: dict | None = None) -> dict | list:
        try:
            r = self._http.put(f"{self.BASE_URL}{path}", headers=self._headers, json=strip_astral(data or {}))
            return self._handle(r)
        except httpx.TimeoutException:
            return {"error": "Request timed out — check your connection"}
        except httpx.HTTPError as e:
            return {"error": f"Network error: {e}"}

    def delete(self, path: str) -> dict:
        try:
            r = self._http.delete(f"{self.BASE_URL}{path}", headers=self._headers)
            if r.status_code == 204:
                return {"success": True}
            return self._handle(r)
        except httpx.TimeoutException:
            return {"error": "Request timed out — check your connection"}
        except httpx.HTTPError as e:
            return {"error": f"Network error: {e}"}

    def _handle(self, r: httpx.Response) -> dict | list:
        if r.status_code == 404:
            return {"error": f"Not found (404): {r.text or 'no body'}"}
        if r.status_code == 403:
            return {"error": f"Forbidden (403) — check API key permissions: {r.text or 'no body'}"}
        if r.status_code >= 500:
            return {"error": f"Assembla server error ({r.status_code}): {r.text or 'no body'}"}
        if r.status_code >= 400:
            return {"error": f"Request failed ({r.status_code}): {r.text}"}
        if not r.content:
            return {"success": True}
        return r.json()


def init_client(api_key: str, api_secret: str) -> None:
    global _instance
    _instance = AssemblaClient(api_key, api_secret)
    atexit.register(lambda: _instance._http.close() if _instance else None)


def get_client() -> AssemblaClient:
    if _instance is None:
        raise RuntimeError("Client not initialized. Call init_client() first.")
    return _instance
