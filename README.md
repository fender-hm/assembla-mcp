# assembla-mcp

MCP server for [Assembla](https://www.assembla.com) — exposes tickets, milestones, merge requests, tags, and components as Claude tools.

## Install

```bash
pip install assembla-mcp
```

## Setup

### 1. Get API credentials

In Assembla: **Profile → API Credentials** → copy your API key and secret.

### 2. Configure Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "assembla": {
      "command": "assembla-mcp",
      "env": {
        "ASSEMBLA_API_KEY": "your-api-key",
        "ASSEMBLA_API_SECRET": "your-api-secret"
      }
    }
  }
}
```

> **Tip:** If `assembla-mcp` is not on your `PATH`, use the full binary path instead. Run `which assembla-mcp` to find it.

Restart Claude Code. At the start of each session call `set_active_space` to pick your workspace.

## Tools

### Spaces
| Tool | Description |
|------|-------------|
| `list_spaces` | List all accessible spaces |
| `set_active_space` | Set the active space by ID or name |
| `list_space_tools` | List git repos and other tools in the active space |
| `set_active_tool` | Set the active space tool (required before merge request tools) |

### Tickets
| Tool | Description |
|------|-------------|
| `list_tickets` | List tickets (filter by status, milestone, component, tag) |
| `get_ticket` | Get a ticket by number |
| `create_ticket` | Create a new ticket |
| `update_ticket` | Update ticket fields |
| `delete_ticket` | Delete a ticket |

### Milestones
| Tool | Description |
|------|-------------|
| `list_milestones` | List milestones |
| `get_milestone` | Get a milestone by ID |
| `create_milestone` | Create a milestone |
| `update_milestone` | Update milestone fields |
| `delete_milestone` | Delete a milestone |

### Tags
| Tool | Description |
|------|-------------|
| `list_ticket_tags` | List tags on a ticket |
| `add_ticket_tag` | Add a tag to a ticket |
| `remove_ticket_tag` | Remove a tag from a ticket |

### Components
| Tool | Description |
|------|-------------|
| `list_components` | List components in the active space (read-only) |

### Merge Requests

> **Prerequisites:** call `list_space_tools` then `set_active_tool` before using these tools.
> Merge requests in Assembla are scoped to a git repo (space tool), not just a space.

| Tool | Description |
|------|-------------|
| `list_merge_requests` | List merge requests (filter by `status`: `open`, `closed`, `ignored`) |
| `get_merge_request` | Get a merge request by ID |
| `create_merge_request` | Create a merge request (`source_cleanup` deletes the source branch on merge/ignore) |
| `update_merge_request` | Update title, description, target branch, or source cleanup |
| `approve_merge_request` | Approve by upvoting a version (latest by default) |
| `ignore_merge_request` | Ignore (reject) a merge request without merging |
| `merge_merge_request` | Apply and close a merge request |
| `list_mr_comments` | List comments on a merge request |
| `add_mr_comment` | Add a comment to a merge request |

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## License

MIT