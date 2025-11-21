import httpx
from typing import Any
import logging
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

lfx = os.getenv("LIFXKEY")

# Asynchronously POST a JSON payload to a URL and log any HTTP errors.
async def fetch_url(url: str, headers: dict[str, str], payload: dict[str, Any], bulb_name: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
           response = await client.post(url, headers=headers, json=payload)
           response.raise_for_status()
           return f"The {bulb_name} bulb toggled successfully"
        
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e}")
            return f"Failed to toggle the {bulb_name} bulb: {e}"

#toggle bedroom bulb
async def bedroom_bulb(duration: int = 0) -> str:
    duration = int(duration) if duration else 0
    
    # Input validation
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds")

    payload = {"duration": duration}
    bulb_name = "label:Bedroom"

    #lifx endpoint
    url = f"https://api.lifx.com/v1/lights/{bulb_name}/toggle"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }

    fetch_response = await fetch_url(url, headers, payload, "Bedroom")
    return fetch_response

#toggle restroom bulb
async def restroom_bulb(duration: int = 0) -> str:
    duration = int(duration) if duration else 0
    
    # Input validation
    if duration < 0 or duration > 100:
        raise ValueError("Error: duration must be between 0 and 100 seconds")

    payload = {"duration": duration}
    bulb_name = "label:Restroom"
    
    #lifx endpoint
    url = f"https://api.lifx.com/v1/lights/{bulb_name}/toggle"

    headers = {
        "Authorization": f"Bearer {lfx}",
        "Content-Type": "application/json"
    }
    
    fetch_response = await fetch_url(url, headers, payload, "Restroom")
    return fetch_response