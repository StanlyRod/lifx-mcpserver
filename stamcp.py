from typing import Any
import httpx
import requests
import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from lifx_controls import bedroom_bulb, restroom_bulb

load_dotenv()

mcp = FastMCP(name="sta-mcpserver")

@mcp.tool()
async def toggle_bedroom_light_bulb(duration: int = 0) -> None:
    """
    Toggle the bedroom LIFX light on or off asynchronously.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    await bedroom_bulb(duration)

@mcp.tool()
async def toggle_restroom_light_bulb(duration: int = 0) -> None:
    """
    Toggle the restroom LIFX light on or off asynchronously.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """

    # Implement restroom bulb toggle logic here
    await restroom_bulb(duration)

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
