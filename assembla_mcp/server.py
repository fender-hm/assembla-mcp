from __future__ import annotations
import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from assembla_mcp.client import init_client
from assembla_mcp.tools import spaces, tickets, milestones, tags, components, merge_requests


def create_server() -> FastMCP:
    mcp = FastMCP("assembla-mcp")
    spaces.register(mcp)
    tickets.register(mcp)
    milestones.register(mcp)
    tags.register(mcp)
    components.register(mcp)
    merge_requests.register(mcp)
    return mcp


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("ASSEMBLA_API_KEY", "")
    api_secret = os.environ.get("ASSEMBLA_API_SECRET", "")
    if not api_key or not api_secret:
        print(
            "Error: ASSEMBLA_API_KEY and ASSEMBLA_API_SECRET environment variables must be set.\n"
            "Copy .env.example to .env and fill in your credentials.",
            file=sys.stderr,
        )
        sys.exit(1)
    init_client(api_key, api_secret)
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()