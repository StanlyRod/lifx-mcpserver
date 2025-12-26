import httpx
from typing import Any
import logging
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

lfx = os.getenv("LIFXKEY")

# Asynchronously httprequest a JSON payload to a URL and log any HTTP errors..
async def fetch_url(method: str, url: str, headers: dict[str, str], payload: dict[str, Any], bulb_name: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
           response = await client.request(method, url, headers=headers, json=payload, timeout=20)
           response.raise_for_status()
           return f"The {bulb_name} bulb action was successfully"
        
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            return f"Failed to perform the action on {bulb_name} bulb: {e}"
        except httpx.ConnectTimeout as e:
            logging.error(f"Connection timeout for {bulb_name}: {e}")
            return f"Failed to perfom the action on {bulb_name} bulb: connection timeout."
        except httpx.TimeoutException as e:
            # Covers all timeout types
            logging.error(f"General timeout for {bulb_name}: {e}")
            return f"Failed to perform the action on {bulb_name} bulb: request timed out."
        except Exception as e:
            # Last-resort catch-all for unexpected errors
            logging.error(f"Unexpected error for {bulb_name}: {e}")
            return f"An unexpected error occurred while performing the action on {bulb_name} bulb."


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


# #toggle bedroom bulb
# async def bedroom_bulb(duration: int = 0) -> str:
#     duration = int(duration) if duration else 0
    
#     # Input validation
#     if duration < 0 or duration > 100:
#         raise ValueError("Error: duration must be between 0 and 100 seconds")

#     payload = {"duration": duration}
#     bulb_name = "label:Bedroom"

#     #lifx endpoint
#     url = f"https://api.lifx.com/v1/lights/{bulb_name}/toggle"

#     headers = {
#         "Authorization": f"Bearer {lfx}",
#         "Content-Type": "application/json"
#     }

#     fetch_response = await fetch_url("POST", url, headers, payload, "Bedroom")
#     return fetch_response


# #toggle restroom bulb
# async def restroom_bulb(duration: int = 0) -> str:
#     duration = int(duration) if duration else 0
    
#     # Input validation
#     if duration < 0 or duration > 100:
#         raise ValueError("Error: duration must be between 0 and 100 seconds")

#     payload = {"duration": duration}
#     bulb_name = "label:Restroom"
    
#     #lifx endpoint
#     url = f"https://api.lifx.com/v1/lights/{bulb_name}/toggle"

#     headers = {
#         "Authorization": f"Bearer {lfx}",
#         "Content-Type": "application/json"
#     }
    
#     fetch_response = await fetch_url("POST", url, headers, payload, "Restroom")
#     return fetch_response


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