"""
Mapbox Agent - Geocodes addresses to coordinates using Mapbox Geocoding API
"""
from uagents import Agent, Context
from models import MapboxRequest, MapboxResponse
import aiohttp
import os


MAPBOX_TOKEN = os.getenv("MAPBOX_API_KEY")


def _validate_geocoding_response(data: dict) -> dict:
    """Validate and extract coordinates from Mapbox API response."""
    assert isinstance(data, dict), "Response data must be a dictionary"
    
    if data.get("features") and len(data["features"]) > 0:
        feature = data["features"][0]
        coords = feature["geometry"]["coordinates"]

        return {
            "latitude": coords[1],  # Mapbox returns [lng, lat]
            "longitude": coords[0],
            "full_address": feature["properties"].get("full_address", "")
        }
    
    raise ValueError("No coordinates found in response")


async def geocode_address(address: str) -> dict:
    """
    Use Mapbox Geocoding API to convert address to coordinates.
    
    Args:
        address: The address to geocode
        
    Returns:
        dict with latitude, longitude, and full_address, or error message
        
    Raises:
        ValueError: If address cannot be geocoded
        Exception: If API request fails
    """
    assert isinstance(address, str), "Address must be a string"
    assert MAPBOX_TOKEN, "Mapbox token must be configured"
    
    url = "https://api.mapbox.com/search/geocode/v6/forward"
    params = {
        "q": address,
        "access_token": MAPBOX_TOKEN,
        "limit": 1,  # Only get top result
        "country": "PT"  # Restrict to PT addresses
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Mapbox API error {resp.status}: {text}")

            data = await resp.json()
            return _validate_geocoding_response(data)


def create_mapbox_agent(port: int = 8004):
    """Create and configure the Mapbox geocoding agent."""
    agent = Agent(
        name="mapbox_agent",
        port=port,
        seed="mapbox_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Mapbox Agent started at {ctx.agent.address}")

    @agent.on_message(model=MapboxRequest)
    async def handle_geocode_request(ctx: Context, sender: str, msg: MapboxRequest):
        """Handle geocoding requests with robust error handling."""
        try:
            result = await geocode_address(msg.address)
            await ctx.send(sender, MapboxResponse(
                address=result["full_address"],
                latitude=result["latitude"],
                longitude=result["longitude"],
                session_id=msg.session_id
            ))
        except Exception:
            # Silently fail - don't send response for invalid addresses
            pass

    return agent