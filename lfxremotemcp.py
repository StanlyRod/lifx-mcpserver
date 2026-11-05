from typing import Any
import logging
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from dotenv import load_dotenv
import lfx_controlers as stc
import sys

load_dotenv()

mcp = MCPServer(name="lifx-mcpserver", version="0.1.0")

@mcp.tool()
async def turn_bedroom_light_on(duration: int = 0) -> str:
    """Turn on the LIFX light labeled Bedroom.

    Use when the user asks to turn on the bedroom light.
    duration: Fade time in whole seconds, from 0 to 100.
    Defaults to 0 for an immediate change.
    """
    return await stc.bulb_on("Bedroom", duration)

@mcp.tool()
async def turn_bedroom_light_off(duration: int = 0) -> str:
    """Turn off the LIFX light labeled Bedroom.

    Use when the user asks to turn off the bedroom light.
    duration: Fade time in whole seconds, from 0 to 100.
    Defaults to 0 for an immediate change.
    """
    return await stc.bulb_off("Bedroom", duration)

@mcp.tool()
async def turn_restroom_light_on(duration: int = 0) -> str:
    """Turn on the LIFX light labeled Restroom.

    Use when the user asks to turn on the restroom light.
    duration: Fade time in whole seconds, from 0 to 100.
    Defaults to 0 for an immediate change.
    """
    return await stc.bulb_on("Restroom", duration)

@mcp.tool()
async def turn_restroom_light_off(duration: int = 0) -> str:
    """Turn off the LIFX light labeled Restroom.

    Use when the user asks to turn off the restroom light.
    duration: Fade time in whole seconds, from 0 to 100.
    Defaults to 0 for an immediate change.
    """
    return await stc.bulb_off("Restroom", duration)

@mcp.tool()
async def toggle_sweep_all_bulbs(duration: float = 0.0) -> str:
    """Toggle power for all LIFX lights accessible to this API key.

    Use only when the user explicitly requests toggling all lights.
    This affects all lights, including lights outside Bedroom and Restroom.
    Do not use for requests to explicitly turn all lights on or off,
    because toggling does not guarantee that requested final state.

    duration: Fade time in seconds, from 0 to 100.
    Fractional seconds are allowed. Defaults to 0 for an immediate change.
    """

    response_sb = await stc.sweep_all_bulbs(duration)
    return response_sb

@mcp.tool()
async def set_bulb_brightness(intensity: int, bulb_name: str) -> str:
    """Set the brightness percentage of one named LIFX light.

    Use when the user asks to brighten, dim, or set a light's brightness.
    intensity: Whole-number percentage from 0 to 100.
    For example, pass 50 for 50% brightness.
    bulb_name: Light label, such as Bedroom or Restroom.
    Supply the label alone, without a 'label:' prefix.
    Ask which light if the target cannot be determined from context.

    This tool changes brightness; it does not explicitly set power.
    """

    response_bright = await stc.brightness_bulb(intensity, bulb_name)
    return response_bright

@mcp.tool()
async def set_bulb_color(color: str, bulb_name: str) -> str:
    """Set the color of one named LIFX light.

    Use when the user asks to change a light's color.
    color: Nonempty LIFX color string, such as 'red', 'blue',
    or 'hue:120 saturation:1.0 brightness:1.0'.
    bulb_name: Light label, such as Bedroom or Restroom.
    Supply the label alone, without a 'label:' prefix.
    Ask which light if the target cannot be determined from context.

    This tool does not explicitly set power. A color string containing
    brightness also changes brightness.
    """

    response_color = await stc.bulb_color(color, bulb_name)
    return response_color

@mcp.tool()
async def get_all_lights_status(only_connected: bool = True) -> list[dict[str, Any]]:
    """List LIFX lights with power, brightness, and color information.

    Use when the user asks which lights are available, which lights are on
    or off, or what brightness and color the lights have.

    Returns each light's ID, name, connectivity, power state, brightness
    percentage, approximate color name, and raw color values.

    only_connected: Include only connected lights by default, whether on
    or off. Set False to include disconnected lights, whose reported
    states may be outdated.

    Color names are estimates. Brightness is the configured level and may
    be nonzero even when a light is off. This tool only reads information.
    """
    try:
        return await stc.list_lights_status(only_connected=only_connected)
    except RuntimeError as exc:
        raise ToolError(str(exc)) from None


def main():
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=3131,
        stateless_http=True,
        json_response=True,
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down lifx MCP server...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
