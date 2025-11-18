from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="sta-mcpserver",
    version="1.0.0",
    description="A MCP server for STA")



def main():
    print("Hello from sta-mcpserver!")


if __name__ == "__main__":
    main()
