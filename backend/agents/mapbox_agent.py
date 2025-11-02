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


def _is_valid_portugal_location(lat: float, lon: float, expected_region: str = None) -> bool:
    """Validate that coordinates are within Portugal and optionally in expected region."""
    # Portugal bounds (approximate)
    # Latitude: 36.8°N to 42.2°N
    # Longitude: -9.5°W to -6.2°W
    
    if not (36.8 <= lat <= 42.2 and -9.5 <= lon <= -6.2):
        return False
    
    # Region-specific validation
    if expected_region:
        region_lower = expected_region.lower()
        
        # Algarve region: roughly 37.0°N to 37.5°N, -8.5°W to -7.0°W
        # Expanded bounds to include nearby areas
        if "algarve" in region_lower or any(city in region_lower for city in ["portimão", "portimao", "faro", "lagos", "alvor", "praia da rocha"]):
            if not (36.8 <= lat <= 37.6 and -8.7 <= lon <= -7.0):
                return False
        
        # Lisbon region: roughly 38.6°N to 39.0°N, -9.5°W to -9.0°W
        elif "lisboa" in region_lower or "lisbon" in region_lower:
            if not (38.6 <= lat <= 39.0 and -9.5 <= lon <= -9.0):
                return False
        
        # Porto region: roughly 41.0°N to 41.3°N, -8.7°W to -8.4°W
        elif "porto" in region_lower:
            if not (41.0 <= lat <= 41.3 and -8.7 <= lon <= -8.4):
                return False
    
    return True


def _get_region_hint(location: str) -> str:
    """Get region hint for common Portuguese locations to improve geocoding accuracy."""
    location_lower = location.lower()
    
    # Algarve region cities
    algarve_cities = ["portimão", "portimao", "faro", "lagos", "tavira", "albufeira", 
                      "vilamoura", "olhão", "loulé", "alvor", "praia da rocha"]
    if any(city in location_lower for city in algarve_cities):
        return "Algarve"
    
    # Lisbon region
    lisbon_cities = ["lisboa", "lisbon", "cascais", "sintra", "oeiras"]
    if any(city in location_lower for city in lisbon_cities):
        return "Lisboa"
    
    # Porto region
    porto_cities = ["porto", "gaia", "matosinhos", "maia"]
    if any(city in location_lower for city in porto_cities):
        return "Porto"
    
    return ""


async def geocode_address(address: str, context_location: str = None) -> dict:
    """
    Use Mapbox Geocoding API to convert address to coordinates.
    Uses multiple fallback strategies for better success rate.
    
    Args:
        address: The address to geocode
        context_location: Original search location for disambiguation (e.g., "Portimão")
        
    Returns:
        dict with latitude, longitude, and full_address, or error message
        
    Raises:
        ValueError: If address cannot be geocoded
        Exception: If API request fails
    """
    assert isinstance(address, str), "Address must be a string"
    assert MAPBOX_TOKEN, "Mapbox token must be configured"
    
    region_hint = _get_region_hint(context_location) if context_location else None
    
    # Strategy 1: Try with full address + region context
    query_strategies = []
    
    if context_location and region_hint:
        # Special handling for "Portimão Cidade, Portimão" type addresses
        # These often geocode to wrong locations, so simplify the query
        address_lower = address.lower()
        if "portimão cidade" in address_lower or "portimao cidade" in address_lower:
            # Strategy 1: Just use "Portimão, Algarve" to get the city center
            query_strategies.append(f"{context_location}, {region_hint}, Portugal")
            # Strategy 2: Try with common Portimão area names
            query_strategies.append("Portimão, Algarve, Portugal")
        else:
            # Strategy 1: Full address with region
            query_strategies.append(f"{address}, {region_hint}, Portugal")
            # Strategy 2: Context location + region (if address contains context)
            if context_location.lower() in address.lower():
                query_strategies.append(f"{context_location}, {region_hint}, Portugal")
        # Strategy 3: Just context location + region
        query_strategies.append(f"{context_location}, {region_hint}, Portugal")
    elif context_location:
        query_strategies.append(f"{address}, {context_location}, Portugal")
        query_strategies.append(f"{context_location}, Portugal")
    
    # Strategy 4: Original address (fallback)
    query_strategies.append(address)
    
    # Try each strategy until we find a valid result
    for query in query_strategies:
        url = "https://api.mapbox.com/search/geocode/v6/forward"
        params = {
            "q": query,
            "access_token": MAPBOX_TOKEN,
            "limit": 5,  # Get multiple results to validate
            "country": "PT"  # Restrict to PT addresses
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        continue  # Try next strategy
                    
                    data = await resp.json()
                    
                    if not data.get("features"):
                        continue  # Try next strategy
                    
                    # If we have context, try to find a result in the expected region
                    if context_location and region_hint:
                        best_match = None
                        fallback_match = None
                        
                        for feature in data["features"]:
                            coords = feature["geometry"]["coordinates"]
                            lat, lon = coords[1], coords[0]
                            
                            feature_address = feature["properties"].get("full_address", "").lower()
                            feature_context = feature["properties"].get("context", [])
                            
                            # Validate coordinates are in Portugal first
                            if not _is_valid_portugal_location(lat, lon):
                                continue
                            
                            # Keep first valid Portuguese result as fallback
                            if fallback_match is None:
                                fallback_match = feature
                            
                            # Check if coordinates are in expected region
                            if _is_valid_portugal_location(lat, lon, region_hint):
                                # Check if address contains context location
                                if context_location.lower() in feature_address:
                                    return _validate_geocoding_response({"features": [feature]})
                                
                                # For Algarve, also check context metadata
                                if region_hint == "Algarve":
                                    # Check context for Faro district or Algarve
                                    for ctx_item in feature_context:
                                        if isinstance(ctx_item, dict):
                                            region = ctx_item.get("region", "").lower()
                                            district = ctx_item.get("district", "").lower()
                                            if "faro" in region or "algarve" in region or "faro" in district:
                                                return _validate_geocoding_response({"features": [feature]})
                                
                                # Keep best match if coordinates are in region
                                if best_match is None:
                                    best_match = feature
                        
                        # Return best match in region, or fallback if no strict match
                        if best_match:
                            return _validate_geocoding_response({"features": [best_match]})
                        elif fallback_match:
                            # Fallback: Use first valid Portuguese result even if outside region
                            # This ensures we don't lose properties due to overly strict validation
                            fallback_coords = fallback_match["geometry"]["coordinates"]
                            fallback_lat, fallback_lon = fallback_coords[1], fallback_coords[0]
                            # Only use fallback if it's reasonably close (within Portugal mainland)
                            if _is_valid_portugal_location(fallback_lat, fallback_lon):
                                return _validate_geocoding_response({"features": [fallback_match]})
                    
                    # No context or no strict validation needed - return first result
                    return _validate_geocoding_response(data)
        
        except Exception:
            continue  # Try next strategy
    
    # All strategies failed
    raise ValueError(f"Could not geocode address '{address}' with any strategy")


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
            result = await geocode_address(msg.address, msg.context_location)
            await ctx.send(sender, MapboxResponse(
                address=result["full_address"],
                latitude=result["latitude"],
                longitude=result["longitude"],
                session_id=msg.session_id
            ))
        except Exception as e:
            ctx.logger.warning(f"Geocoding failed for '{msg.address}': {e}")
            # Silently fail - don't send response for invalid addresses
            pass

    return agent