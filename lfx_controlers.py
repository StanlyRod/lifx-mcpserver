import httpx
from typing import Any
import logging
import os
from dotenv import load_dotenv
import asyncio

logger = logging.getLogger(__name__)

# Shared HTTP client
_http_client: httpx.AsyncClient | None = None

load_dotenv()

lfx = (os.getenv("LIFXKEY") or "").strip()
if not lfx:
    raise RuntimeError(
        "LIFXKEY is required. Set it in the environment or in a .env file "
        "before starting the server."
    )

def get_http_client() -> httpx.AsyncClient:
    global _http_client

    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=httpx.Timeout(20.0), limits=httpx.Limits(max_connections=10, max_keepalive_connections=5, keepalive_expiry=30.0))

    return _http_client


async def close_http_client() -> None:
    global _http_client

    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


# Send an asynchronous LIFX request and report failures.
async def fetch_url(method: str, url: str, headers: dict[str, str], payload: dict[str, Any], bulb_name: str) -> str:
    try:
        client = get_http_client()
        response = await client.request(method=method, url=url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("LIFX request succeeded | bulb=%s | status=%s", bulb_name, response.status_code)
        return f"Successfully performed action on {bulb_name} bulb."

    except httpx.HTTPStatusError as e:
        logger.error("LIFX HTTP error | bulb=%s | status=%s", bulb_name, e.response.status_code)
        return f"Failed to control {bulb_name}: HTTP {e.response.status_code}"

    except httpx.TimeoutException:
        logger.error("LIFX timeout | bulb=%s", bulb_name)
        return f"Failed to control {bulb_name}: timeout."

    except httpx.RequestError as e:
        logger.error("LIFX network error | bulb=%s | type=%s", bulb_name, type(e).__name__)
        return f"Failed to control {bulb_name}: network error."

    except Exception:
        logger.exception("Unexpected LIFX error | bulb=%s", bulb_name)
        return f"Unexpected error controlling {bulb_name}."


# Turn a specific bulb ON
async def bulb_on(bulb_name: str, duration: int = 0) -> str:
    duration = int(duration) if duration else 0
    
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds")

    payload = {"power": "on", "duration": duration}
    selected_bulb = f"label:{bulb_name.capitalize()}"
    url = f"https://api.lifx.com/v1/lights/{selected_bulb}/state"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    return await fetch_url("PUT", url, headers, payload, bulb_name.capitalize())


# Turn a specific bulb OFF
async def bulb_off(bulb_name: str, duration: int = 0) -> str:
    duration = int(duration) if duration else 0
    
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds")

    payload = {"power": "off", "duration": duration}
    selected_bulb = f"label:{bulb_name.capitalize()}"
    url = f"https://api.lifx.com/v1/lights/{selected_bulb}/state"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    return await fetch_url("PUT", url, headers, payload, bulb_name.capitalize())


#toggle sweep bulb
async def sweep_all_bulbs(duration: float = 0.0) -> str:
    # --- Validate duration ---
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds.")

    # Payload (converted to JSON later)
    payload = {
        "duration": duration
    }

    url = "https://api.lifx.com/v1/lights/all/toggle"


    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    fetch_response = await fetch_url("POST", url, headers, payload, "All bulbs")
    return fetch_response


# Set bulb brightness
async def brightness_bulb(intensity: int, bulb_name: str) -> str:
    # Input validation: Ensure intensity is between 0% and 100%
    if intensity < 0 or intensity > 100:
        raise ValueError("Error the brightness level have to be set between 0 and 100")
    
    brightness_level = intensity / 100.0

    selected_bulb_name = f"label:{bulb_name.capitalize()}"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    # Payload
    payload = {
        "brightness": brightness_level
    }
    
    # API endpoint
    url = f"https://api.lifx.com/v1/lights/{selected_bulb_name}/state"

    fetch_response = await fetch_url("PUT", url, headers, payload, bulb_name)
    return fetch_response
    

# set bulb color
async def bulb_color(color_value: str, bulb_name: str) -> str:
    # Validate color_value
    if not color_value or color_value.strip() == "":
        raise ValueError("Error: color_value argument is required.")
    
    selected_bulb_name = f"label:{bulb_name.capitalize()}"

    # Build payload
    payload = {
        "color": color_value
    }

    # API endpoint
    url = f"https://api.lifx.com/v1/lights/{selected_bulb_name}/state"

    # Headers
    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    # Call your existing fetch_url() from the image
    fetch_response = await fetch_url("PUT", url, headers, payload, bulb_name)

    return fetch_response