from __future__ import annotations
import atexit
import httpx
from typing import Optional

_instance: Optional["AssemblaClient"] = None


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
            r = self._http.post(f"{self.BASE_URL}{path}", headers=self._headers, json=data)
            return self._handle(r)
        except httpx.TimeoutException:
            return {"error": "Request timed out — check your connection"}
        except httpx.HTTPError as e:
            return {"error": f"Network error: {e}"}

    def put(self, path: str, data: dict | None = None) -> dict | list:
        try:
            r = self._http.put(f"{self.BASE_URL}{path}", headers=self._headers, json=data or {})
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
            return {"error": "Not found (404)"}
        if r.status_code == 403:
            return {"error": "Forbidden (403) — check API key permissions"}
        if r.status_code >= 500:
            return {"error": f"Assembla server error ({r.status_code}) — try again"}
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
