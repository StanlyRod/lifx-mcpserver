from typing import Any
import httpx
import requests
import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import sta_controlers as stc

load_dotenv()

mcp = FastMCP(name="sta-mcpserver", host="0.0.0.0", port=3131, stateless_http=True, json_response=True)

@mcp.tool()
async def toggle_bedroom_light_bulb(duration: int = 0) -> str:
    """
    Toggle the bedroom LIFX light on or off asynchronously.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    response_bb = await stc.bedroom_bulb(duration)
    return response_bb

@mcp.tool()
async def toggle_restroom_light_bulb(duration: int = 0) -> str:
    """
    Toggle the restroom LIFX light on or off asynchronously.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """

    response_rb = await stc.restroom_bulb(duration)
    return response_rb

def main():
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down STA MCP server...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
