from uagents import Agent, Context
from models import ResearchRequest, ResearchResponse, PropertyListing
from clients.brigthdata import BrightDataClient
import aiohttp, os, json
import re


ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_URL = "https://api.asi1.ai/v1/chat/completions"
BRIGHTDATA_TOKEN = os.getenv("BRIGHT_DATA_API_KEY")


def extract_first_image_from_markdown(markdown: str) -> str | None:
    """Extract the first relevant image URL from markdown content."""
    assert isinstance(markdown, str), "Markdown content must be a string"
    
    # Filter for likely property images (avoid icons, logos, etc.)
    img_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    matches = re.findall(img_pattern, markdown)

    for url in matches:
        # Skip small images, icons, and logos
        if any(skip in url.lower() for skip in ['icon', 'logo', 'avatar', 'badge', 'button']):
            continue
        # Skip very small dimensions in URL
        if any(size in url.lower() for size in ['16x16', '32x32', '48x48', '64x64']):
            continue
        return url

    return None


def filter_results_by_location(search_results: list, required_location: str) -> list:
    """Filter search results to include only real estate listings in the specified location."""
    assert isinstance(search_results, list), "Search results must be a list"
    assert isinstance(required_location, str), "Location must be a string"
    
    filtered = []
    location_lower = required_location.lower()
    valid_domains = ['idealista.pt', 'imovirtual.com', 'casasapo.pt', 'olx.pt']

    for result in search_results:
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        link = result.get("link", "").lower()

        # Must be from real estate website and contain location
        is_valid_site = any(domain in link for domain in valid_domains)
        has_location = location_lower in title or location_lower in description or location_lower in link

        if is_valid_site and has_location:
            filtered.append(result)

    return filtered


def _build_search_query(requirements) -> str:
    """Construct optimized search query from user requirements for Portuguese Algarve market."""
    parts = []
    
    # Use Portuguese location - default to Algarve if not specified
    location_lower = requirements.location.lower() if requirements.location else ""
    if not any(city in location_lower for city in ['algarve', 'faro', 'loulé', 'portimão', 'lagos', 'albufeira', 'tavira', 'silves']):
        # If not already in Algarve, add it for focus
        parts.append("Algarve Portugal")
    else:
        parts.append(requirements.location)
    
    # Portuguese property type mapping
    if requirements.bedrooms is not None:
        if requirements.bedrooms == 0:
            parts.append("T0")  # Studio
        elif requirements.bedrooms == 1:
            parts.append("T1")  # 1 bedroom
        elif requirements.bedrooms == 2:
            parts.append("T2")  # 2 bedroom
        elif requirements.bedrooms == 3:
            parts.append("T3")  # 3 bedroom
        else:
            parts.append(f"{requirements.bedrooms} quartos")
    else:
        parts.append("quartos")  # rooms

    # Focus on long-term rentals (arrendamento)
    parts.append("arrendamento")
    
    # Portuguese portals to target
    parts.append("site:idealista.pt OR site:imovirtual.com OR site:casasapo.pt OR site:olx.pt")

    if requirements.budget_max:
        if requirements.budget_max < 1000000:
            parts.append(f"até {requirements.budget_max} euros")
        else:
            mil = requirements.budget_max / 1000000
            parts.append(f"até {mil:.1f} milhões euros")

    return " ".join(parts)


async def _generate_llm_summary(search_results: list, requirements, original_query: str) -> str:
    """Generate conversational summary using ASI-1 LLM."""
    assert isinstance(search_results, list), "Search results must be a list"
    
    headers = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Format search results for LLM
    results_text = ""
    for i, result in enumerate(search_results[:8], 1):
        title = result.get("title", "")
        description = result.get("description", "")
        link = result.get("link", "")
        results_text += f"{i}. {title}\n"
        if description:
            results_text += f"   {description}\n"
        results_text += f"   Link: {link}\n\n"

    # Build requirement summary
    req_parts = [requirements.location]
    if requirements.bedrooms:
        req_parts.append(f"{requirements.bedrooms} bedrooms")
    if requirements.bathrooms:
        req_parts.append(f"{requirements.bathrooms} bathrooms")
    if requirements.budget_max:
        mil = requirements.budget_max / 1000000
        req_parts.append(f"budget under ${mil:.1f}M")
    req_text = ", ".join(req_parts)

    body = {
        "model": "asi-1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly real estate assistant. Based on search results, "
                    "provide a natural, conversational summary of available properties. "
                    "Mention 2-3 specific listings with addresses and key details. "
                    "Keep it warm and helpful, 3-4 sentences max. "
                    "DO NOT mention the total number of listings in your response."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User is looking for: {req_text}\n\n"
                    f"Search results:\n{results_text}\n"
                    "Summarize what properties are available. Don't mention how many listings there are."
                ),
            },
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ASI_URL, headers=headers, json=body) as resp:
                if resp.status != 200:
                    return f"Here are some property listings in {requirements.location}. Check the results for details!"

                res = await resp.json()
                if "choices" in res and res["choices"]:
                    return res["choices"][0]["message"]["content"]
                else:
                    return f"Here are some property listings in {requirements.location}. Check the results for details!"
    except Exception:
        return f"Here are some property listings in {requirements.location}. Check the results for details!"


async def _scrape_property_images(results: list, brightdata) -> list:
    """Extract property images from search results using web scraping."""
    assert isinstance(results, list), "Results must be a list"
    result_images = []

    for idx, result in enumerate(results[:5]):
        result_url = result.get("link", "")
        if result_url and ("olx.pt" in result_url or "idealista.pt" in result_url):
            try:
                scrape_result = await brightdata.call("scrape_as_markdown", {"url": result_url})
                if scrape_result["success"]:
                    markdown = scrape_result.get("output", "")
                    image_url = extract_first_image_from_markdown(markdown)
                    if image_url:
                        result_images.append({"index": idx, "image_url": image_url})
            except Exception:
                continue  # Continue with next result if scraping fails

    return result_images


def _parse_property_listings(data: dict, location: str) -> tuple[list, list]:
    """Parse property data from various response formats."""
    assert isinstance(data, dict), "Data must be a dictionary"
    
    properties = []
    organic_results = []

    if "organic" in data:
        organic_results = data.get("organic", [])

    if "properties" in data:
        for prop_data in data.get("properties", []):
            try:
                listing = PropertyListing(
                    address=prop_data.get("address", "Unknown"),
                    city=prop_data.get("city", location),
                    price=prop_data.get("price"),
                    bedrooms=prop_data.get("bedrooms"),
                    bathrooms=prop_data.get("bathrooms"),
                    sqft=prop_data.get("sqft"),
                    description=prop_data.get("description"),
                    url=prop_data.get("url"),
                    latitude=None,
                    longitude=None
                )
                properties.append(listing)
            except Exception:
                continue  # Skip invalid property data

    return properties, organic_results


async def _handle_search_results(result: dict, req, session_id: str, sender, ctx) -> ResearchResponse:
    """Process search results and generate appropriate response."""
    if not result["success"]:
        return ResearchResponse(
            properties=[],
            search_summary=f"Search failed: {result.get('error', 'Unknown error')}",
            total_found=0,
            session_id=session_id
        )

    # Parse response and extract property listings
    raw_output = result.get("output", "")
    properties = []
    organic_results = []
    result_images = []

    try:
        data = json.loads(raw_output)
        properties, organic_results = _parse_property_listings(data, req.location)

        # Filter by location if we have organic results
        if organic_results:
            organic_results = filter_results_by_location(organic_results, req.location)
            if not organic_results:
                return ResearchResponse(
                    properties=[],
                    search_summary=f"No properties found specifically in {req.location}. Try expanding to nearby areas.",
                    total_found=0,
                    session_id=session_id,
                    raw_search_results=[],
                    top_result_image_url=None,
                    result_images=[]
                )

            # Scrape images from top results
            result_images = await _scrape_property_images(organic_results, ctx.brightdata)

    except json.JSONDecodeError:
        pass  # Continue with empty results

    # Generate summary based on available data
    if organic_results and len(organic_results) > 0:
        summary = await _generate_llm_summary(organic_results, req, "")
    elif properties:
        summary = f"Properties in {req.location}"
        if req.bedrooms:
            summary += f" with {req.bedrooms} bedrooms"
        if req.budget_max:
            mil = req.budget_max / 1000000
            summary += f" under ${mil:.1f}M"
    else:
        summary = f"No properties found matching your criteria in {req.location}"

    # Prepare response data
    total_results = len(organic_results) if organic_results else len(properties)
    top_result_image = result_images[0]["image_url"] if result_images else None

    return ResearchResponse(
        properties=properties,
        search_summary=summary,
        total_found=total_results,
        session_id=session_id,
        raw_search_results=organic_results if organic_results else None,
        top_result_image_url=top_result_image,
        result_images=result_images if result_images else None
    )


def create_research_agent(port: int = 8002):
    """Create and configure the research agent for property intelligence gathering."""
    agent = Agent(
        name="research_agent",
        port=port,
        seed="research_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    agent.brightdata = BrightDataClient()

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Research Agent started at {ctx.agent.address}")

    @agent.on_message(model=ResearchRequest)
    async def handle_request(ctx: Context, sender: str, msg: ResearchRequest):
        """Handle property research requests with comprehensive search and analysis."""
        req = msg.requirements
        prompt = _build_search_query(req)
        
        # Execute search via Bright Data
        result = await agent.brightdata.call("search_engine", {"query": prompt, "engine": "google"})
        
        # Process results and generate response
        response = await _handle_search_results(result, req, msg.session_id, sender, ctx)
        await ctx.send(sender, response)

    return agent


def parse_zillow_markdown(markdown: str, requirements) -> list:
    """Parse Zillow markdown to extract property listings with validation."""
    assert isinstance(markdown, str), "Markdown must be a string"
    assert hasattr(requirements, 'budget_max'), "Requirements must have budget_max attribute"
    
    properties = []
    lines = markdown.split("\n")
    current_property = {}

    for line in lines:
        # Extract address and URL from markdown links
        if ("St," in line or "Ave," in line or "Rd," in line or
            "Blvd," in line or "APT" in line or "Way," in line):

            if current_property and "address" in current_property:
                try:
                    listing = PropertyListing(**current_property)
                    properties.append(listing)
                except Exception:
                    pass
                current_property = {}

            if "](https://" in line:
                start = line.find("[") + 1
                end = line.find("](")
                address = line[start:end].strip()

                url_start = line.find("](") + 2
                url_end = line.find(")", url_start)
                url = line[url_start:url_end]

                current_property["address"] = address
                current_property["url"] = url

                # Extract city
                if ", CA " in address or ",CA " in address:
                    parts = address.split(",")
                    if len(parts) >= 2:
                        current_property["city"] = parts[-2].strip()

        # Extract property details
        elif line.strip().startswith("$") and current_property:
            price_str = line.strip().replace("$", "").replace(",", "")
            try:
                current_property["price"] = int(price_str)
            except ValueError:
                pass

        elif "**" in line and ("bd" in line or "ba" in line) and current_property:
            # Extract bedrooms
            if "bds" in line or "bd" in line:
                try:
                    parts = line.split("**")
                    for i, part in enumerate(parts):
                        if i+1 < len(parts) and "bd" in parts[i+1]:
                            current_property["bedrooms"] = int(part.strip())
                            break
                except (ValueError, IndexError):
                    pass

            # Extract bathrooms
            if "ba" in line:
                try:
                    parts = line.split("**")
                    for i, part in enumerate(parts):
                        if (i+1 < len(parts) and "ba" in parts[i+1] and 
                            "bd" not in parts[i+1]):
                            current_property["bathrooms"] = float(part.strip())
                            break
                except (ValueError, IndexError):
                    pass

            # Extract square footage
            if "sqft" in line:
                try:
                    sqft_idx = line.find("sqft")
                    before_sqft = line[:sqft_idx]
                    parts = before_sqft.split("**")
                    sqft_str = parts[-2].replace(",", "").strip()
                    current_property["sqft"] = int(sqft_str)
                except (ValueError, IndexError):
                    pass

    # Add final property
    if current_property and "address" in current_property:
        try:
            listing = PropertyListing(**current_property)
            properties.append(listing)
        except Exception:
            pass

    # Filter by requirements
    filtered = []
    for prop in properties:
        if requirements.budget_max and prop.price and prop.price > requirements.budget_max:
            continue
        if requirements.bedrooms and prop.bedrooms and prop.bedrooms != requirements.bedrooms:
            continue
        if requirements.bathrooms and prop.bathrooms and prop.bathrooms < requirements.bathrooms:
            continue
        filtered.append(prop)

    return filtered