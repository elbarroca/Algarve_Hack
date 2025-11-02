"""
Estate Search Main - Coordinator with REST API
"""
import asyncio
from uagents import Agent, Context, Model, Bureau
from typing import Dict, Any, Optional
from models import (
    ScopingRequest,
    ScopingResponse,
    ResearchRequest,
    ResearchResponse,
    GeneralRequest,
    GeneralResponse,
    MapboxRequest,
    MapboxResponse,
    LocalDiscoveryRequest,
    LocalDiscoveryResponse,
    CommunityAnalysisRequest,
    CommunityAnalysisResponse,
    ProberRequest,
    ProberResponse,
)
from agents.scoping_agent import create_scoping_agent
from agents.research_agent import create_research_agent
from agents.base_agent import create_general_agent
from agents.mapbox_agent import create_mapbox_agent
from agents.local_agent import create_local_discovery_agent
from agents.community_agent import create_community_analysis_agent
from agents.prober_agent import create_prober_agent
from agents.vapi_agent import create_vapi_agent, VapiRequest, VapiResponse
from llm_client import SimpleLLMAgent

# REST API Models
class ChatRequest(Model):
    message: str
    session_id: str


class ChatResponse(Model):
    status: str
    data: Dict[str, Any]


class NegotiateRequest(Model):
    address: str
    name: str
    email: str
    additional_info: str = ""
    # Detailed listing data - when provided, skips prober agent and goes straight to VAPI
    listing_data: Optional[Dict[str, Any]] = None  # Full property listing details
    # Required fields in listing_data for direct VAPI call:
    # - contact_phone: Phone number to call (required)
    # - price: Monthly rent or sale price
    # - title: Property title/description
    # Optional but recommended:
    # - bedrooms, bathrooms, sqft
    # - amenities, features
    # - availability_date
    # - description
    skip_research: bool = False  # Set to True to skip prober and go straight to VAPI


class NegotiateResponse(Model):
    success: bool
    message: str
    leverage_score: float
    next_actions: list
    call_summary: str = ""
    # Structured outcomes from VAPI call
    availability_date: Optional[str] = None
    price_flexibility: Optional[str] = None
    tenant_requirements: Optional[str] = None


def main():
    print("=" * 60)
    print("Estate Search System Starting")
    print("=" * 60)

    # Create all agents
    scoping_agent = create_scoping_agent(port=8001)
    research_agent = create_research_agent(port=8002)
    general_agent = create_general_agent(port=8003)
    mapbox_agent = create_mapbox_agent(port=8004)
    local_discovery_agent = create_local_discovery_agent(port=8005)
    community_analysis_agent = create_community_analysis_agent(port=8006)
    prober_agent = create_prober_agent(port=8007)
    vapi_agent = create_vapi_agent(port=8008)

    # Create coordinator agent
    coordinator = Agent(
        name="coordinator",
        port=8080,
        seed="coordinator_seed",
        endpoint=["http://localhost:8080/submit"]
    )

    # Store agent addresses
    scoping_address = scoping_agent.address
    research_address = research_agent.address
    general_address = general_agent.address
    mapbox_address = mapbox_agent.address
    local_discovery_address = local_discovery_agent.address
    community_analysis_address = community_analysis_agent.address
    prober_address = prober_agent.address
    vapi_address = vapi_agent.address

    # Session storage
    sessions = {}
    prober_sessions = {}  # Separate storage for prober responses
    vapi_sessions = {}  # Separate storage for vapi responses

    # Create LLM summarizer
    llm_summarizer = SimpleLLMAgent(
        name="NegotiationSummarizer",
        system_prompt="You are an expert real estate negotiation analyst. Summarize negotiation conversations concisely."
    )

    @coordinator.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info("=" * 60)
        ctx.logger.info("Coordinator started")
        ctx.logger.info(f"Scoping Agent: {scoping_address}")
        ctx.logger.info(f"Research Agent: {research_address}")
        ctx.logger.info(f"Local Discovery Agent: {local_discovery_address}")
        ctx.logger.info(f"Community Analysis Agent: {community_analysis_address}")
        ctx.logger.info("=" * 60)

    @coordinator.on_message(model=ScopingResponse)
    async def handle_scoping(ctx: Context, sender: str, msg: ScopingResponse):
        ctx.logger.info(f"Received scoping response for session {msg.session_id}")
        ctx.logger.info(f"DEBUG - is_general_question: {msg.is_general_question}")
        ctx.logger.info(f"DEBUG - general_question: {msg.general_question}")
        ctx.logger.info(f"DEBUG - is_complete: {msg.is_complete}")

        if msg.session_id not in sessions:
            sessions[msg.session_id] = {}

        sessions[msg.session_id]["scoping"] = msg

        # Route based on intent
        if msg.is_general_question and msg.general_question:
            # Forward to general agent with context
            ctx.logger.info(f"Forwarding to general agent with question: {msg.general_question}")

            # Get last search location from session for context
            last_location = sessions[msg.session_id].get("last_search_location")
            context = f"The user's last property search was in: {last_location}" if last_location else None

            await ctx.send(
                general_address,
                GeneralRequest(
                    question=msg.general_question,
                    session_id=msg.session_id,
                    context=context
                )
            )
        elif msg.is_complete and msg.requirements:
            # Save last search location for context
            sessions[msg.session_id]["last_search_location"] = msg.requirements.location

            # Forward to research agent for property search
            ctx.logger.info(f"Forwarding to research agent")
            await ctx.send(
                research_address,
                ResearchRequest(
                    requirements=msg.requirements,
                    session_id=msg.session_id
                )
            )

            # Also send to community analysis agent if we have a community name
            if msg.community_name:
                ctx.logger.info(f"Forwarding to community analysis agent for: {msg.community_name}")
                await ctx.send(
                    community_analysis_address,
                    CommunityAnalysisRequest(
                        location_name=msg.community_name,
                        session_id=msg.session_id
                    )
                )

    @coordinator.on_message(model=ResearchResponse)
    async def handle_research(ctx: Context, sender: str, msg: ResearchResponse):
        ctx.logger.info(f"Received research response for session {msg.session_id}")

        if msg.session_id not in sessions:
            sessions[msg.session_id] = {}

        sessions[msg.session_id]["research"] = msg
        sessions[msg.session_id]["geocoded_results"] = []
        sessions[msg.session_id]["geocoding_count"] = 0
        sessions[msg.session_id]["poi_results"] = []
        sessions[msg.session_id]["poi_count"] = 0

        # If we have formatted properties with full addresses, geocode all of them (up to 10)
        if msg.formatted_properties_json and len(msg.formatted_properties_json) > 0:
            # Limit to 10 for comprehensive results
            properties_to_geocode = msg.formatted_properties_json[:10]
            ctx.logger.info(f"Geocoding {len(properties_to_geocode)} properties with full addresses")

            # Get original search location for context
            original_location = sessions[msg.session_id].get("last_search_location", "")
            
            for idx, prop in enumerate(properties_to_geocode):
                # Extract full address from location data (formatted properties have detailed location info)
                location = prop.get("location", {})
                address = location.get("full_address") or location.get("address") or prop.get("address", "")

                if address:
                    ctx.logger.info(f"Geocoding property {idx + 1}: {address} (context: {original_location})")
                    await ctx.send(
                        mapbox_address,
                        MapboxRequest(
                            address=address,
                            session_id=f"{msg.session_id}__{idx}",  # Unique ID per result
                            context_location=original_location  # Pass context for disambiguation
                        )
                    )
        else:
            ctx.logger.info("No search results to geocode")

    @coordinator.on_message(model=MapboxResponse)
    async def handle_mapbox(ctx: Context, sender: str, msg: MapboxResponse):
        ctx.logger.info(f"Received Mapbox response for session {msg.session_id}")

        # Parse session ID to check if it's a multi-geocoding request
        if "__" in msg.session_id:
            # This is a geocoded result for cycling through listings
            base_session_id, idx_str = msg.session_id.split("__", 1)
            idx = int(idx_str)

            if base_session_id not in sessions:
                sessions[base_session_id] = {}

            if "geocoded_results" not in sessions[base_session_id]:
                sessions[base_session_id]["geocoded_results"] = []

            # Store this geocoded result
            if not msg.error:
                ctx.logger.info(f"Geocoded result {idx + 1}: {msg.address} -> ({msg.latitude}, {msg.longitude})")
                
                # Validate coordinates are in expected region if we have context
                base_session_id_check = base_session_id if "__" in msg.session_id else msg.session_id
                original_location = sessions.get(base_session_id_check, {}).get("last_search_location", "")
                if original_location:
                    # Check if coordinates match expected region
                    region_hint = None
                    location_lower = original_location.lower()
                    if any(city in location_lower for city in ["portimão", "portimao", "faro", "lagos", "alvor"]):
                        region_hint = "Algarve"
                    
                    if region_hint:
                        from agents.mapbox_agent import _is_valid_portugal_location
                        if not _is_valid_portugal_location(msg.latitude, msg.longitude, region_hint):
                            ctx.logger.warning(f"❌ Geocoded result {idx + 1} is outside expected region: {msg.address} -> ({msg.latitude}, {msg.longitude})")
                            # Still store it but mark as potentially incorrect
                            ctx.logger.warning(f"   Expected region: {region_hint}, but got coordinates outside bounds")
                
                sessions[base_session_id]["geocoded_results"].append({
                    "index": idx,
                    "latitude": msg.latitude,
                    "longitude": msg.longitude,
                    "address": msg.address
                })

                # Trigger POI search for this location
                ctx.logger.info(f"Triggering POI search for listing {idx + 1}")
                await ctx.send(
                    local_discovery_address,
                    LocalDiscoveryRequest(
                        latitude=msg.latitude,
                        longitude=msg.longitude,
                        session_id=base_session_id,
                        listing_index=idx
                    )
                )
            else:
                ctx.logger.warning(f"Geocoding error for result {idx + 1}: {msg.error}")

            sessions[base_session_id]["geocoding_count"] = sessions[base_session_id].get("geocoding_count", 0) + 1

        else:
            # Legacy single result geocoding
            if msg.session_id not in sessions:
                sessions[msg.session_id] = {}

            sessions[msg.session_id]["mapbox"] = msg

            if msg.error:
                ctx.logger.warning(f"Mapbox geocoding error: {msg.error}")
            else:
                ctx.logger.info(f"Geocoded: {msg.address} -> ({msg.latitude}, {msg.longitude})")

    @coordinator.on_message(model=LocalDiscoveryResponse)
    async def handle_local_discovery(ctx: Context, sender: str, msg: LocalDiscoveryResponse):
        ctx.logger.info(f"Received POI response for session {msg.session_id}, listing {msg.listing_index}: {len(msg.pois)} POIs")

        if msg.session_id not in sessions:
            sessions[msg.session_id] = {}

        if "poi_results" not in sessions[msg.session_id]:
            sessions[msg.session_id]["poi_results"] = []

        # Store POIs for this listing
        sessions[msg.session_id]["poi_results"].append({
            "listing_index": msg.listing_index,
            "pois": [poi.dict() for poi in msg.pois]
        })

        sessions[msg.session_id]["poi_count"] = sessions[msg.session_id].get("poi_count", 0) + 1

    @coordinator.on_message(model=GeneralResponse)
    async def handle_general(ctx: Context, sender: str, msg: GeneralResponse):
        ctx.logger.info(f"Received general response for session {msg.session_id}")

        if msg.session_id not in sessions:
            sessions[msg.session_id] = {}

        sessions[msg.session_id]["general"] = msg

    @coordinator.on_message(model=CommunityAnalysisResponse)
    async def handle_community_analysis(ctx: Context, sender: str, msg: CommunityAnalysisResponse):
        ctx.logger.info(f"Received community analysis response for session {msg.session_id}")

        if msg.session_id not in sessions:
            sessions[msg.session_id] = {}

        sessions[msg.session_id]["community_analysis"] = msg

    @coordinator.on_message(model=ProberResponse)
    async def handle_prober_response(ctx: Context, sender: str, msg: ProberResponse):
        ctx.logger.info(f"Received prober response for session {msg.session_id}")
        ctx.logger.info(f"   Found {len(msg.findings)} findings, leverage score: {msg.leverage_score}/10")
        prober_sessions[msg.session_id] = msg

    @coordinator.on_message(model=VapiResponse)
    async def handle_vapi_response(ctx: Context, sender: str, msg: VapiResponse):
        ctx.logger.info(f"Received Vapi response for session {msg.session_id}")
        ctx.logger.info(f"   Status: {msg.status}, Call ID: {msg.call_id}")
        vapi_sessions[msg.session_id] = msg

    # Health check endpoint
    class HealthResponse(Model):
        status: str
    
    @coordinator.on_rest_get("/health", HealthResponse)
    async def handle_health(ctx: Context) -> HealthResponse:
        return HealthResponse(status="ok")
    
    @coordinator.on_rest_post("/api/chat", ChatRequest, ChatResponse)
    async def handle_chat(ctx: Context, req: ChatRequest) -> ChatResponse:
        ctx.logger.info(f"REST request from session {req.session_id}: {req.message}")

        # Initialize session
        if req.session_id not in sessions:
            sessions[req.session_id] = {}

        try:
            # Clear old responses for this request
            sessions[req.session_id].pop("scoping", None)
            sessions[req.session_id].pop("research", None)

            # ALWAYS send every new user message to scoping agent first
            # The scoping agent will determine if we need to gather more info or search
            ctx.logger.info("Routing message to scoping agent")
            await ctx.send(
                scoping_address,
                ScopingRequest(
                    user_message=req.message,
                    session_id=req.session_id
                )
            )

            # Wait for scoping response
            for _ in range(60):
                if "scoping" in sessions[req.session_id]:
                    break
                await asyncio.sleep(0.5)
            else:
                return ChatResponse(
                    status="error",
                    data={"message": "Timeout waiting for scoping agent"}
                )

            scoping_msg = sessions[req.session_id]["scoping"]

            # Handle general question
            if scoping_msg.is_general_question:
                ctx.logger.info("Waiting for general agent response")

                for _ in range(60):
                    if "general" in sessions[req.session_id]:
                        break
                    await asyncio.sleep(0.5)

                if "general" in sessions[req.session_id]:
                    general_msg = sessions[req.session_id]["general"]
                    return ChatResponse(
                        status="success",
                        data={
                            "requirements": {},
                            "properties": [],
                            "search_summary": general_msg.answer,
                            "total_found": 0
                        }
                    )

            # Handle property search
            if scoping_msg.is_complete and scoping_msg.requirements:
                ctx.logger.info("Waiting for research results")

                for _ in range(960):  # Increased to 480 seconds (960 * 0.5s) to handle long scraping operations
                    if "research" in sessions[req.session_id]:
                        break
                    await asyncio.sleep(0.5)

                # Also wait for community analysis if we have a community name
                if scoping_msg.community_name:
                    ctx.logger.info("Waiting for community analysis results")
                    for _ in range(60):
                        if "community_analysis" in sessions[req.session_id]:
                            break
                        await asyncio.sleep(0.5)

                if "research" in sessions[req.session_id]:
                    research_msg = sessions[req.session_id]["research"]

                    # Wait for Mapbox geocoding if we have search results
                    if research_msg.formatted_properties_json and len(research_msg.formatted_properties_json) > 0:
                        results_count = min(len(research_msg.formatted_properties_json), 10)
                        ctx.logger.info(f"Waiting for {results_count} geocoding results")

                        # Wait up to 15 seconds for all geocoding to complete
                        for _ in range(30):
                            geocoding_count = sessions[req.session_id].get("geocoding_count", 0)
                            if geocoding_count >= results_count:
                                ctx.logger.info(f"All {results_count} results geocoded")
                                break
                            await asyncio.sleep(0.5)
                        else:
                            ctx.logger.warning(f"Timeout: only {sessions[req.session_id].get('geocoding_count', 0)}/{results_count} results geocoded")

                        # Wait for POI searches to complete (up to 20 more seconds)
                        ctx.logger.info(f"Waiting for POI results for {results_count} listings")
                        for _ in range(40):
                            poi_count = sessions[req.session_id].get("poi_count", 0)
                            if poi_count >= results_count:
                                ctx.logger.info(f"All {results_count} POI searches complete")
                                break
                            await asyncio.sleep(0.5)
                        else:
                            ctx.logger.warning(f"Timeout: only {sessions[req.session_id].get('poi_count', 0)}/{results_count} POI searches completed")

                    # Merge geocoded data, images, and POIs into formatted_properties_json
                    enhanced_results = []
                    geocoded_results = sessions[req.session_id].get("geocoded_results", [])
                    result_images = research_msg.result_images if research_msg.result_images else []
                    poi_results = sessions[req.session_id].get("poi_results", [])

                    ctx.logger.info(f"🔍 Merging data - Geocoded: {len(geocoded_results)}, Images: {len(result_images)}, POI results: {len(poi_results)}")

                    # Use formatted_properties_json (detailed property data) instead of raw_search_results
                    formatted_props = research_msg.formatted_properties_json if research_msg.formatted_properties_json else []

                    for idx, prop in enumerate(formatted_props):
                        enhanced_prop = dict(prop)  # Copy the original property

                        # Find matching geocoded data
                        geocoded = next((g for g in geocoded_results if g["index"] == idx), None)

                        if geocoded:
                            # Validate coordinates are in expected region before using them
                            original_location = sessions[req.session_id].get("last_search_location", "")
                            if original_location:
                                from agents.mapbox_agent import _is_valid_portugal_location, _get_region_hint
                                region_hint = _get_region_hint(original_location)
                                if region_hint:
                                    if not _is_valid_portugal_location(geocoded["latitude"], geocoded["longitude"], region_hint):
                                        ctx.logger.warning(f"⚠️ Rejecting geocoded coordinates for property {idx + 1}: outside expected region {region_hint}")
                                        geocoded = None  # Reject wrong coordinates
                            
                            if geocoded:
                                # Add coordinates to the property
                                enhanced_prop["latitude"] = geocoded["latitude"]
                                enhanced_prop["longitude"] = geocoded["longitude"]
                                # Also update location object if it exists
                                if "location" not in enhanced_prop:
                                    enhanced_prop["location"] = {}
                                enhanced_prop["location"]["latitude"] = geocoded["latitude"]
                                enhanced_prop["location"]["longitude"] = geocoded["longitude"]

                        else:
                            # Geocoding failed or was rejected - try to use coordinates from scraped data
                            location = enhanced_prop.get("location", {})
                            if isinstance(location, dict):
                                scraped_lat = location.get("latitude")
                                scraped_lon = location.get("longitude")
                                if scraped_lat and scraped_lon:
                                    # Validate scraped coordinates are in Portugal
                                    from agents.mapbox_agent import _is_valid_portugal_location
                                    original_location = sessions[req.session_id].get("last_search_location", "")
                                    if original_location:
                                        from agents.mapbox_agent import _get_region_hint
                                        region_hint = _get_region_hint(original_location)
                                        if region_hint and _is_valid_portugal_location(scraped_lat, scraped_lon, region_hint):
                                            enhanced_prop["latitude"] = scraped_lat
                                            enhanced_prop["longitude"] = scraped_lon
                                            ctx.logger.info(f"✅ Using scraped coordinates for property {idx + 1}: ({scraped_lat}, {scraped_lon})")
                                        elif _is_valid_portugal_location(scraped_lat, scraped_lon):
                                            # Fallback: valid Portugal coordinates
                                            enhanced_prop["latitude"] = scraped_lat
                                            enhanced_prop["longitude"] = scraped_lon
                                            ctx.logger.info(f"✅ Using scraped coordinates for property {idx + 1}: ({scraped_lat}, {scraped_lon})")
                                    else:
                                        if _is_valid_portugal_location(scraped_lat, scraped_lon):
                                            enhanced_prop["latitude"] = scraped_lat
                                            enhanced_prop["longitude"] = scraped_lon
                                            ctx.logger.info(f"✅ Using scraped coordinates for property {idx + 1}: ({scraped_lat}, {scraped_lon})")
                                else:
                                    ctx.logger.warning(f"⚠️ No coordinates available for property {idx + 1} (geocoding failed, no scraped data)")

                        # Add image URL if available for this property
                        image_data = next((img for img in result_images if img["index"] == idx), None)
                        if image_data:
                            enhanced_prop["image_url"] = image_data["image_url"]
                            ctx.logger.info(f"Added image to property {idx + 1}")

                        # Add POIs if available for this property
                        poi_data = next((p for p in poi_results if p["listing_index"] == idx), None)
                        if poi_data:
                            enhanced_prop["pois"] = poi_data["pois"]
                            ctx.logger.info(f"✅ Added {len(poi_data['pois'])} POIs to property {idx + 1}")
                        else:
                            enhanced_prop["pois"] = []
                            ctx.logger.warning(f"⚠️ No POI data found for property {idx + 1}")

                        # IMPORTANT: Add to results array
                        enhanced_results.append(enhanced_prop)

                    ctx.logger.info(f"📊 Total enhanced properties: {len(enhanced_results)}")
                    for idx, prop in enumerate(enhanced_results):
                        location = prop.get("location", {})
                        address = location.get("full_address") or location.get("address") or prop.get("address", "No address")
                        ctx.logger.info(f"   Property {idx + 1}: {address[:80]}, POIs: {len(prop.get('pois', []))}")

                    # Build top_result_coordinates from first geocoded result
                    top_result_coords = None
                    if len(enhanced_results) > 0 and "latitude" in enhanced_results[0]:
                        first_prop = enhanced_results[0]
                        location = first_prop.get("location", {})
                        address = location.get("full_address") or location.get("address") or first_prop.get("address", "")
                        top_result_coords = {
                            "latitude": first_prop["latitude"],
                            "longitude": first_prop["longitude"],
                            "address": address,
                            "image_url": first_prop.get("image_url")
                        }

                    # Build community analysis data if available
                    community_data = None
                    if "community_analysis" in sessions[req.session_id]:
                        community_msg = sessions[req.session_id]["community_analysis"]
                        community_data = {
                            "location": community_msg.location,
                            "overall_score": community_msg.overall_score,
                            "overall_explanation": community_msg.overall_explanation,
                            "safety_score": community_msg.safety_score,
                            "positive_stories": community_msg.positive_stories,
                            "negative_stories": community_msg.negative_stories,
                            "school_rating": community_msg.school_rating,
                            "school_explanation": community_msg.school_explanation,
                            "housing_price_per_square_foot": community_msg.housing_price_per_square_foot,
                            "average_house_size_square_foot": community_msg.average_house_size_square_foot
                        }

                    return ChatResponse(
                        status="success",
                        data={
                            "requirements": scoping_msg.requirements.dict(),
                            "properties": [p.dict() for p in research_msg.properties],
                            "search_summary": research_msg.search_summary,
                            "total_found": research_msg.total_found,
                            "top_result_coordinates": top_result_coords,
                            "raw_search_results": enhanced_results,
                            "community_analysis": community_data
                        }
                    )

            # Return scoping conversation (only if not searching)
            if scoping_msg.is_complete and scoping_msg.requirements:
                # Should have returned research results above - something went wrong
                return ChatResponse(
                    status="error",
                    data={"message": "Research agent did not respond in time"}
                )

            return ChatResponse(
                status="success",
                data={
                    "requirements": scoping_msg.requirements.dict() if scoping_msg.requirements else {},
                    "properties": [],
                    "search_summary": scoping_msg.agent_message,
                    "total_found": 0
                }
            )

        except Exception as e:
            ctx.logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return ChatResponse(
                status="error",
                data={"message": str(e)}
            )

    @coordinator.on_rest_post("/api/negotiate", NegotiateRequest, NegotiateResponse)
    async def handle_negotiate(ctx: Context, req: NegotiateRequest) -> NegotiateResponse:
        ctx.logger.info(f"🤝 Negotiation request for: {req.address}")
        ctx.logger.info(f"   User: {req.name} ({req.email})")

        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())

        try:
            # Check if we should skip research and go straight to VAPI
            has_contact_phone = req.listing_data and (
                req.listing_data.get("contact_phone") or
                req.listing_data.get("seller_phone")
            )
            should_skip_research = req.skip_research or has_contact_phone

            if should_skip_research and has_contact_phone:
                ctx.logger.info("✅ Detailed listing data provided with contact phone")
                ctx.logger.info("⚡ Skipping prober agent - going straight to VAPI call")

                # Build intelligence from listing data
                contact_phone = req.listing_data.get("contact_phone") or req.listing_data.get("seller_phone")
                ctx.logger.info(f"📞 Contact phone: {contact_phone}")

                # Create minimal intelligence structure for VAPI
                intelligence_dict = {
                    "leverage_score": 5.0,  # Neutral score since no research
                    "overall_assessment": f"Direct inquiry about property at {req.address}. "
                                        f"Student seeking information on availability, pricing, and tenant requirements.",
                    "findings": [
                        {
                            "category": "direct_inquiry",
                            "summary": f"Direct contact with listing agent for {req.address}",
                            "details": f"Property details: {req.listing_data.get('title', 'N/A')}. "
                                     f"Price: €{req.listing_data.get('price', 'N/A')}/month. "
                                     f"Seeking information about availability and tenant requirements.",
                            "leverage_score": 5.0,
                            "source_url": None
                        }
                    ],
                    "property": {
                        "address": req.address,
                        "contact_phone": contact_phone,
                        "seller_phone": req.listing_data.get("seller_phone"),
                        "seller_name": req.listing_data.get("seller_name"),
                        "contact_email": req.listing_data.get("contact_email"),
                        **req.listing_data  # Include all listing data
                    }
                }

                # Skip directly to VAPI call
                leverage_score = 5.0
                next_actions = [
                    "Call will be placed to listing agent",
                    "Ask about availability dates",
                    "Discuss pricing and flexibility",
                    "Understand tenant requirements"
                ]

            else:
                # Original flow: use prober agent for research
                ctx.logger.info(f"📤 Sending probe request to prober agent...")
                await ctx.send(
                    prober_address,
                    ProberRequest(
                        address=req.address,
                        session_id=session_id
                    )
                )

                # Wait for prober response (120 seconds timeout - increased from 60)
                for _ in range(240):  # 120 seconds (240 * 0.5s)
                    if session_id in prober_sessions:
                        break
                    await asyncio.sleep(0.5)
                else:
                    ctx.logger.error("❌ Timeout waiting for prober response")
                    return NegotiateResponse(
                        success=False,
                        message="Timeout waiting for property intelligence. Please try again.",
                        leverage_score=0.0,
                        next_actions=[]
                    )

                # Get prober response
                prober_result = prober_sessions.pop(session_id)

                # Extract contact info from listing data if provided
                contact_phone = None
                seller_phone = None
                seller_name = None
                contact_email = None

                if req.listing_data:
                    contact_phone = req.listing_data.get("contact_phone") or req.listing_data.get("seller_phone")
                    seller_phone = req.listing_data.get("seller_phone")
                    seller_name = req.listing_data.get("seller_name")
                    contact_email = req.listing_data.get("contact_email")
                    ctx.logger.info(f"📞 Found contact info from listing:")
                    ctx.logger.info(f"   Contact Phone: {contact_phone}")
                    ctx.logger.info(f"   Seller Phone: {seller_phone}")
                    ctx.logger.info(f"   Seller Name: {seller_name}")
                else:
                    ctx.logger.warning(f"⚠️ No listing data provided - will use fallback phone number")

                # Convert findings to dict format for Vapi
                findings_data = [
                    {
                        "category": f.category,
                        "summary": f.summary,
                        "leverage_score": f.leverage_score,
                        "details": f.details,
                        "source_url": f.source_url
                    }
                    for f in prober_result.findings
                ]

                # Use prober results for intelligence
                intelligence_dict = {
                    "leverage_score": prober_result.leverage_score,
                    "overall_assessment": prober_result.overall_assessment,
                    "findings": findings_data,
                    # Include property data in intelligence so Vapi agent can access contact info
                    "property": {
                        "address": req.address,
                        # Contact info from listing data
                        "contact_phone": contact_phone,
                        "seller_phone": seller_phone,
                        "seller_name": seller_name,
                        "contact_email": contact_email,
                        # Include full listing data if provided
                        **(req.listing_data or {})
                    }
                }

                leverage_score = prober_result.leverage_score
                next_actions = []  # Will be generated by LLM later

            # Call Vapi agent to make the negotiation call
            ctx.logger.info("📞 Sending request to Vapi agent...")
            ctx.logger.info(f"   Intelligence score: {leverage_score}/10")
            ctx.logger.info(f"   Contact phone: {intelligence_dict['property'].get('contact_phone', 'N/A')}")

            await ctx.send(
                vapi_address,
                VapiRequest(
                    property_address=req.address,
                    user_name=req.name,
                    user_email=req.email,
                    user_preferences=req.additional_info,
                    intelligence=intelligence_dict,
                    session_id=session_id
                )
            )

            # Wait for Vapi response (30 seconds timeout)
            for _ in range(60):  # 30 seconds (60 * 0.5s)
                if session_id in vapi_sessions:
                    break
                await asyncio.sleep(0.5)
            else:
                ctx.logger.warning("⚠️ Timeout waiting for Vapi response (call may still be in progress)")
                # Continue anyway - call was probably initiated

            vapi_result = vapi_sessions.pop(session_id, None)
            vapi_call_summary = ""
            availability_date = None
            price_flexibility = None
            tenant_requirements = None

            if vapi_result and vapi_result.status == "success":
                ctx.logger.info(f"✅ Vapi call completed! Call ID: {vapi_result.call_id}")
                vapi_call_summary = vapi_result.call_summary or ""
                # Extract structured outcomes from Vapi response
                availability_date = vapi_result.availability_date
                price_flexibility = vapi_result.price_flexibility
                tenant_requirements = vapi_result.tenant_requirements
                ctx.logger.info(f"📊 Extracted outcomes:")
                ctx.logger.info(f"   Availability: {availability_date}")
                ctx.logger.info(f"   Price Flexibility: {price_flexibility}")
                ctx.logger.info(f"   Tenant Requirements: {tenant_requirements}")
            else:
                ctx.logger.warning("⚠️ Vapi call may be in progress")

            # Generate AI summary and next actions (only if we used prober agent)
            if not should_skip_research:
                # We have prober_result, generate detailed summary
                ctx.logger.info("📝 Generating negotiation summary with LLM...")
                summary_prompt = f"""Based on the following property intelligence, create a concise negotiation summary and actionable next steps.

Property: {req.address}
User: {req.name}
Additional Context: {req.additional_info or 'None provided'}

Intelligence Findings ({len(prober_result.findings)} items):
{chr(10).join([f"- {f.category}: {f.summary} (leverage: {f.leverage_score}/10)" for f in prober_result.findings[:5]])}

Overall Assessment: {prober_result.overall_assessment}
Leverage Score: {prober_result.leverage_score}/10

Generate ONLY valid JSON with this exact structure:
{{
  "summary": "A 2-3 sentence summary of the negotiation position and key findings",
  "next_actions": [
    "Specific action item 1",
    "Specific action item 2",
    "Specific action item 3"
  ]
}}

Focus on practical, actionable steps the buyer should take next."""

                summary_result = await llm_summarizer.query_with_json(summary_prompt, temperature=0.5)

                if summary_result.get("success"):
                    summary_data = summary_result.get("data", {})
                    ai_summary = summary_data.get("summary", prober_result.overall_assessment)
                    next_actions = summary_data.get("next_actions", [])
                else:
                    ai_summary = prober_result.overall_assessment
                    next_actions = [
                        "Review the identified leverage points carefully",
                        "Prepare your negotiation strategy based on findings",
                        "Contact the listing agent to initiate discussions"
                    ]

                ctx.logger.info(f"✅ Summary generated with {len(next_actions)} action items")
            else:
                # Skipped research, use simple summary
                ai_summary = intelligence_dict['overall_assessment']
                # next_actions already defined earlier when we set up intelligence_dict
                ctx.logger.info(f"✅ Using direct call summary with {len(next_actions)} action items")

            return NegotiateResponse(
                success=True,
                message=ai_summary,
                leverage_score=leverage_score,  # Use leverage_score variable, not prober_result
                next_actions=next_actions,
                call_summary=vapi_call_summary,
                availability_date=availability_date,
                price_flexibility=price_flexibility,
                tenant_requirements=tenant_requirements
            )

        except Exception as e:
            ctx.logger.error(f"❌ Negotiation error: {e}")
            import traceback
            traceback.print_exc()
            return NegotiateResponse(
                success=False,
                message=f"Error: {str(e)}",
                leverage_score=0.0,
                next_actions=[]
            )

    # Create Bureau to run all agents
    bureau = Bureau(port=8080, endpoint="http://localhost:8080/submit")
    bureau.add(coordinator)
    bureau.add(scoping_agent)
    bureau.add(research_agent)
    bureau.add(general_agent)
    bureau.add(mapbox_agent)
    bureau.add(local_discovery_agent)
    bureau.add(community_analysis_agent)
    bureau.add(prober_agent)
    bureau.add(vapi_agent)

    print("All agents configured")
    print(f"   - REST API: http://localhost:8080/api/chat")
    print(f"   - REST API: http://localhost:8080/api/negotiate")
    print(f"   - Scoping: {scoping_address}")
    print(f"   - Research: {research_address}")
    print(f"   - General: {general_address}")
    print(f"   - Mapbox: {mapbox_address}")
    print(f"   - Local Discovery: {local_discovery_address}")
    print(f"   - Community Analysis: {community_analysis_address}")
    print(f"   - Prober: {prober_address}")
    print(f"   - Vapi: {vapi_address}")
    print("=" * 60)

    bureau.run()


if __name__ == "__main__":
    main()