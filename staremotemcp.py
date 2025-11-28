from typing import Any
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import sta_controlers as stc
import sys

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
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down STA MCP server...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
