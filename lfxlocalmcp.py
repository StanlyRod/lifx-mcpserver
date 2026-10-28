from typing import Any
import httpx
import requests
import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import lfx_controlers as stc

load_dotenv()

mcp = FastMCP(name="sta-mcpserver")

@mcp.tool()
async def turn_bedroom_light_on(duration: int = 0) -> str:
    """
    Turn the bedroom LIFX light ON.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    return await stc.bulb_on("Bedroom", duration)

@mcp.tool()
async def turn_bedroom_light_off(duration: int = 0) -> str:
    """
    Turn the bedroom LIFX light OFF.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    return await stc.bulb_off("Bedroom", duration)

@mcp.tool()
async def turn_restroom_light_on(duration: int = 0) -> str:
    """
    Turn the restroom LIFX light ON.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    return await stc.bulb_on("Restroom", duration)

@mcp.tool()
async def turn_restroom_light_off(duration: int = 0) -> str:
    """
    Turn the restroom LIFX light OFF.
    
    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds (0-100). Defaults to 0.
    """
    return await stc.bulb_off("Restroom", duration)


@mcp.tool()
async def toggle_sweep_all_bulbs(duration: float = 0.0) -> str:
    """
    Toggle all LIFX lights on or off asynchronously.
    
    Parameters
    ----------
    duration : float, optional
        Fade duration in seconds (0-100). Defaults to 0.0.
    """

    response_sb = await stc.sweep_all_bulbs(duration)
    return response_sb

@mcp.tool()
async def set_bulb_brightness(intensity: int, bulb_name: str) -> str:
    """
    Set the brightness of a specified LIFX bulb asynchronously.
    
    Parameters
    ----------
    intensity : int
        Brightness level (0-100).
    bulb_name : str
        Name or label of the bulb to set brightness for.
    """

    response_bright = await stc.brightness_bulb(intensity, bulb_name)
    return response_bright

@mcp.tool()
async def set_bulb_color(color: str, bulb_name: str) -> str:
    """
    Set the color of a specified LIFX bulb asynchronously.
    
    Parameters
    ----------
    color : str
        Color value (e.g., "red", "blue", "hue:120 saturation:1.0 brightness:1.0").
    bulb_name : str
        Name or label of the bulb to set color for.
    """

    response_color = await stc.bulb_color(color, bulb_name)
    return response_color

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
