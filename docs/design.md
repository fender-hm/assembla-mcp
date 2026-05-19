# Assembla MCP Server — Design Spec

**Date:** 2026-05-14  
**Status:** Approved  
**Language:** Python  
**License:** MIT  

---

## Overview

A standalone open-source Python MCP server that exposes Assembla project management resources (tickets, milestones, merge requests, tags, components) as Claude tools. Designed to be lightweight (Python runtime, ~30–50MB idle), easy to install via `uvx`, and easy to contribute to.

---

## Repo Structure

```
assembla-mcp/
├── assembla_mcp/
│   ├── __init__.py
│   ├── server.py            # Entry point — registers all tools, starts MCP server
│   ├── client.py            # Assembla REST API wrapper (auth, HTTP, error handling)
│   ├── state.py             # Session state — active space, cached space list
│   └── tools/
│       ├── spaces.py        # list_spaces, set_active_space, list_space_tools, set_active_tool
│       ├── tickets.py       # list/get/create/update/delete tickets
│       ├── milestones.py    # list/get/create/update/delete milestones
│       ├── tags.py          # list/add/remove tags on tickets
│       ├── components.py    # list components (read-only)
│       └── merge_requests.py# list/get/create/update/approve/decline/delete + comments
├── .env.example
├── pyproject.toml
├── README.md
├── LICENSE
└── .github/
    ├── CONTRIBUTING.md
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## Architecture

**Data flow:**  
`server.py` registers all tools → tool handlers call `client.py` → `client.py` hits `https://api.assembla.com/v1/` with API key+secret headers → results returned as MCP text content.

**Session state:**  
A `State` singleton in `state.py` holds `active_space_id`, `active_tool_id`, and cached lists of spaces and tools. Resets on server restart. No persistence.

**HTTP client:** `httpx` with a 30-second timeout.

---

## Authentication

Two env vars read at startup via `python-dotenv`:

```
ASSEMBLA_API_KEY=your-key
ASSEMBLA_API_SECRET=your-secret
```

Injected as `X-Api-Key` / `X-Api-Secret` headers on every request. If either is missing at startup, the server exits immediately with a clear error message.

---

## Tools (~22 total)

### `spaces`
| Tool | Description |
|------|-------------|
| `list_spaces` | List all spaces the API key has access to |
| `set_active_space` | Set the active space for the session (required before most tools) |
| `list_space_tools` | List git repos and other tools configured in the active space |
| `set_active_tool` | Set the active space tool by ID (required before merge request tools) |

### `tickets`
| Tool | Description |
|------|-------------|
| `list_tickets` | List tickets in active space (supports filters: status, milestone, component, tag) |
| `get_ticket` | Get a single ticket by number or ID |
| `create_ticket` | Create a new ticket |
| `update_ticket` | Update ticket fields (status, assignee, milestone, component, summary, description) |
| `delete_ticket` | Delete a ticket |

### `milestones`
| Tool | Description |
|------|-------------|
| `list_milestones` | List milestones in active space |
| `get_milestone` | Get a single milestone |
| `create_milestone` | Create a milestone |
| `update_milestone` | Update milestone fields |
| `delete_milestone` | Delete a milestone |

### `tags`
| Tool | Description |
|------|-------------|
| `list_ticket_tags` | List tags on a ticket |
| `add_ticket_tag` | Add a tag to a ticket |
| `remove_ticket_tag` | Remove a tag from a ticket |

### `components`
| Tool | Description |
|------|-------------|
| `list_components` | List all components in active space (read-only, for filtering/assigning) |

### `merge_requests`

Merge requests in Assembla are scoped to a space tool (git repo), not just a space. The API path is `/spaces/{space_id}/space_tools/{tool_id}/merge_requests`. Call `list_space_tools` then `set_active_tool` before using these.

| Tool | Description |
|------|-------------|
| `list_merge_requests` | List merge requests (filter by `status`: `open`, `closed`, `ignored`; supports pagination) |
| `get_merge_request` | Get a single merge request |
| `create_merge_request` | Create a merge request |
| `update_merge_request` | Update title, description, target branch |
| `approve_merge_request` | Approve a merge request |
| `decline_merge_request` | Decline a merge request |
| `list_mr_comments` | List comments on a merge request |
| `add_mr_comment` | Add a comment to a merge request |

All tools that operate on a space default to `active_space_id` from session state. An optional `space_id` parameter overrides this per call. Merge request tools additionally fall back to `active_tool_id`; pass `tool_id` explicitly to override.

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Missing API key/secret at startup | Server exits with clear message |
| No active space set | Returns `"No active space. Call set_active_space first."` |
| 404 from Assembla API | Returns `"Not found (404): <response body>"` |
| 403 from Assembla API | Returns `"Forbidden (403) — check API key permissions: <response body>"` |
| 5xx from Assembla API | Returns `"Assembla server error (5xx): <response body>"` |
| Network timeout (>30s) | Returns `"Request timed out — check your connection"` |

No automatic retries (YAGNI).

---

## Installation & Configuration

### Install
```bash
uvx assembla-mcp
# or
pip install assembla-mcp
```

### Claude Code config (`~/.claude/settings.json`)
```json
{
  "mcpServers": {
    "assembla": {
      "command": "uvx",
      "args": ["assembla-mcp"],
      "env": {
        "ASSEMBLA_API_KEY": "your-key",
        "ASSEMBLA_API_SECRET": "your-secret"
      }
    }
  }
}
```

---

## Packaging

```toml
[project]
name = "assembla-mcp"
requires-python = ">=3.10"
dependencies = ["mcp", "httpx", "python-dotenv"]

[project.scripts]
assembla-mcp = "assembla_mcp.server:main"
```

Published to PyPI so `uvx assembla-mcp` works out of the box.

---

## Open-Source Setup

- **License:** MIT
- **README:** Overview, install, config, tool list, contributing guide
- **CONTRIBUTING.md:** "Add a tool in 5 steps" walkthrough
- **Issue templates:** Bug report, feature request
- **No CI required initially** — add GitHub Actions later when tests exist