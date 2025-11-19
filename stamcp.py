from typing import Any
import httpx
import requests
import asyncio
import logging
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(name="sta-mcpserver")

# Asynchronously POST a JSON payload to a URL and log any HTTP errors.
async def fetch_url(url: str, headers: dict[str, str], payload: dict[str, Any]):
    async with httpx.AsyncClient() as client:
        try:
           response = await client.post(url, headers=headers, json=payload)
           response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")


@mcp.tool()
async def toggle_bedroom_light_bulb(duration: int = 0) -> None:
    logging.info("Toggling bedroom light bulb")
    """
    Toggle the LIFX light on or off asynchronously.

    Sends a toggle request to the LIFX Cloud API for the light labeled
    "Bedroom". The light will switch to the opposite state (on → off, off → on).
    A transition duration may be provided.

    Parameters
    ----------
    duration : int, optional
        Fade duration in seconds for the toggle action. Must be between
        0 and 100. Defaults to 0.

    Raises
    ------
    ValueError
        If `duration` is less than 0 or greater than 100.
    httpx.HTTPStatusError
        If the LIFX API returns a non-successful status code.
    EnvironmentError
        If the `LIFXKEY` environment variable is missing.

    Notes
    -----
    - This function does **not return a value**.
    - Requires an environment variable `LIFXKEY` containing a valid
      LIFX API access token.
    - Uses `httpx.AsyncClient` to perform the API request.
    """
    
    duration = int(duration) if duration else 0
    
    # Input validation
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds")

    payload = {"duration": duration}
    bulb_name = "label:Bedroom"
    lfx = os.getenv("LIFXKEY")

    url = f"https://api.lifx.com/v1/lights/{bulb_name}/toggle"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    await fetch_url(url, headers, payload)

def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
