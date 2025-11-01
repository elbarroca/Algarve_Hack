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
    """Filter search results to include only RENTAL properties in the specified location."""
    assert isinstance(search_results, list), "Search results must be a list"
    assert isinstance(required_location, str), "Location must be a string"
    
    filtered = []
    location_lower = required_location.lower()
    valid_domains = ['idealista.pt', 'imovirtual.com', 'casasapo.pt', 'olx.pt']
    
    # Portuguese rental keywords - MUST have these
    rental_keywords = ['arrendamento', 'aluguer', 'rental', 'alugar', 'aluguel']
    # Portuguese sale keywords - MUST NOT have these
    sale_keywords = ['venda', 'comprar', 'buy', 'sale', 'vender']
    
    for result in search_results:
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        link = result.get("link", "").lower()
        
        # Must be from real estate website and contain location
        is_valid_site = any(domain in link for domain in valid_domains)
        has_location = location_lower in title or location_lower in description or location_lower in link
        
        # Check for rental indicators
        has_rental_keyword = any(keyword in title or keyword in description or keyword in link for keyword in rental_keywords)
        # Check for sale indicators - exclude these
        has_sale_keyword = any(keyword in title or keyword in description or keyword in link for keyword in sale_keywords)
        
        # Include if: valid site + location + (has rental keyword OR rental-specific URL pattern) AND NOT sale
        if is_valid_site and has_location and not has_sale_keyword:
            # Check for rental-specific URL patterns
            is_rental_url = any(pattern in link for pattern in ['/arrendamento', '/aluguer', '/rental', '/alugar'])
            
            # Include if has rental keyword OR rental URL pattern
            if has_rental_keyword or is_rental_url:
                filtered.append(result)
    
    return filtered


def _build_search_query(requirements) -> str:
    """Construct optimized search query from user requirements for Portuguese Algarve RENTAL market."""
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

    # CRITICAL: Focus on RENTALS only - explicitly exclude sales
    parts.append("arrendamento")  # Portuguese for rental
    parts.append("-venda")  # Exclude sales
    parts.append("-comprar")  # Exclude "buy"
    
    # Portuguese rental portals with rental-specific sections
    parts.append("site:idealista.pt/arrendamento OR site:imovirtual.com/aluguer OR site:casasapo.pt/aluguer OR site:olx.pt/aluguer")
    
    # Budget filter for rentals (monthly rent, not purchase price)
    if requirements.budget_max:
        # For rentals, budget is typically monthly rent (much lower than purchase price)
        # If budget_max is very high (>50k), likely meant as purchase price, so convert to monthly
        if requirements.budget_max > 50000:
            # Assume annual rent budget, convert to monthly
            monthly_budget = requirements.budget_max / 12
            if monthly_budget < 1000:
                parts.append(f"até {int(monthly_budget)}€/mês")
            else:
                parts.append(f"até {int(monthly_budget/1000)}k€/mês")
        else:
            # Already in monthly rent range
            if requirements.budget_max < 1000:
                parts.append(f"até {requirements.budget_max}€/mês")
            else:
                parts.append(f"até {requirements.budget_max//1000}k€/mês")
    
    # Ensure we're looking for long-term rentals, not short-term
    parts.append("longa duração OR permanente")  # long-term or permanent rental

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

    # Build requirement summary (for RENTAL properties)
    req_parts = [requirements.location]
    if requirements.bedrooms:
        req_parts.append(f"{requirements.bedrooms} bedrooms")
    if requirements.bathrooms:
        req_parts.append(f"{requirements.bathrooms} bathrooms")
    if requirements.budget_max:
        # For rentals, budget is monthly rent
        monthly_budget = requirements.budget_max if requirements.budget_max < 50000 else requirements.budget_max // 12
        req_parts.append(f"monthly rent under {monthly_budget}€")
    req_text = ", ".join(req_parts)

    body = {
        "model": "asi-1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly real estate assistant specializing in RENTAL properties in Portugal. "
                    "Based on search results, provide a natural, conversational summary of available RENTAL properties. "
                    "Mention 2-3 specific rental listings with addresses and key details. "
                    "Always emphasize these are RENTAL properties (not for sale). "
                    "Keep it warm and helpful, 3-4 sentences max. "
                    "DO NOT mention the total number of listings in your response."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"User is looking for RENTAL properties: {req_text}\n\n"
                    f"Search results (all RENTAL properties):\n{results_text}\n"
                    "Summarize what RENTAL properties are available. Emphasize these are for rent, not for sale."
                ),
            },
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ASI_URL, headers=headers, json=body) as resp:
                if resp.status != 200:
                    return f"Here are some RENTAL properties in {requirements.location}. Check the results for details!"

                res = await resp.json()
                if "choices" in res and res["choices"]:
                    return res["choices"][0]["message"]["content"]
                else:
                    return f"Here are some RENTAL properties in {requirements.location}. Check the results for details!"
    except Exception:
        return f"Here are some RENTAL properties in {requirements.location}. Check the results for details!"


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
        summary = f"RENTAL properties in {req.location}"
        if req.bedrooms:
            summary += f" with {req.bedrooms} bedrooms"
        if req.budget_max:
            monthly_budget = req.budget_max if req.budget_max < 50000 else req.budget_max // 12
            summary += f" under {monthly_budget}€/month"
    else:
        summary = f"No RENTAL properties found matching your criteria in {req.location}. Try expanding your search area or adjusting your budget."

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



def parse_portuguese_property_listings(markdown: str, requirements) -> list:
    """Parse real Portuguese property listings from Algarve sources with validation."""
    assert isinstance(markdown, str), "Markdown must be a string"
    assert hasattr(requirements, 'budget_max'), "Requirements must have budget_max attribute"
    
    properties = []
    lines = markdown.split("\n")
    current_property = {}

    # Portuguese Algarve cities for validation
    algarve_cities = ['faro', 'loulé', 'portimão', 'lagos', 'albufeira', 'tavira', 'silves']

    for line in lines:
        line_lower = line.lower().strip()
        
        # Extract address and URL from Portuguese property links
        # Check URL for rental indicators first - skip sale listings
        if any(pattern in line_lower for pattern in ['idealista.pt', 'imovirtual.com', 'casasapo.pt', 'olx.pt']):
            # Check if URL contains sale indicators - skip if so
            if any(sale_indicator in line_lower for sale_indicator in ['/venda/', '/comprar/', 'venda', 'comprar']):
                # Skip sale listings - reset current property and continue
                if current_property:
                    current_property = {}
                continue
            
            if current_property and "address" in current_property:
                try:
                    # Validate Algarve location before adding
                    city = current_property.get("city", "").lower()
                    if any(algarve_city in city for algarve_city in algarve_cities):
                        listing = PropertyListing(**current_property)
                        properties.append(listing)
                except Exception:
                    pass
                current_property = {}

            # Extract URL from markdown links [text](url)
            if "](" in line and "https://" in line:
                start = line.find("](") + 2
                end = line.find(")", start)
                url = line[start:end]
                
                # Extract title/address before the URL
                title_start = line.find("[")
                title_end = line.find("]")
                if title_start != -1 and title_end != -1:
                    title = line[title_start+1:title_end]
                    title_lower = title.lower()
                    
                    current_property["url"] = url
                    current_property["address"] = title
                    
                    # Extract city from title
                    for algarve_city in algarve_cities:
                        if algarve_city in title_lower:
                            current_property["city"] = algarve_city.title()
                            break

                    # Extract property type from title (T0, T1, T2, etc.)
                    type_match = re.search(r'\b(t[0-5])\b', title_lower)
                    if type_match:
                        prop_type = type_match.group(1).upper()
                        if prop_type == 'T0':
                            current_property["bedrooms"] = 0
                        elif prop_type == 'T1':
                            current_property["bedrooms"] = 1
                        elif prop_type == 'T2':
                            current_property["bedrooms"] = 2
                        elif prop_type == 'T3':
                            current_property["bedrooms"] = 3
                        elif prop_type == 'T4':
                            current_property["bedrooms"] = 4
                        elif prop_type == 'T5':
                            current_property["bedrooms"] = 5

        # Portuguese currency (€) - handle patterns like "850 €", "1.200€", etc.
        # For rentals, look for monthly rent indicators like "€/mês", "€/mes", "€/month"
        elif ("€" in line or "eur" in line_lower) and current_property:
            # Check if this is a rental price (monthly)
            is_monthly_rent = any(indicator in line_lower for indicator in ['/mês', '/mes', '/month', 'mensal', 'mensalidade'])
            
            price_match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', line)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(".", "").replace(",", "")
                    price_value = int(price_str)
                    # For rentals, prices are typically monthly (much lower than purchase prices)
                    # If it's marked as monthly or less than 10k, it's likely monthly rent
                    if is_monthly_rent or price_value < 10000:
                        current_property["price"] = price_value  # Monthly rent
                    # If very high (>100k), likely annual rent or purchase price
                    elif price_value > 100000:
                        # For rentals, convert annual to monthly if needed
                        current_property["price"] = price_value // 12
                except ValueError:
                    pass

        # Portuguese bedroom patterns like "2 quartos", "1 quarto"
        elif any(pattern in line_lower for pattern in ['quarto', 'quartos']) and current_property:
            bedroom_match = re.search(r'(\d+)\s*(?:quarto|quartos)', line_lower)
            if bedroom_match:
                try:
                    current_property["bedrooms"] = int(bedroom_match.group(1))
                except ValueError:
                    pass

        # Bathrooms - Portuguese patterns like "1 wc", "2 casas de banho", etc.
        elif any(pattern in line_lower for pattern in ['wc', 'casa de banho', 'banheiro']) and current_property:
            wc_match = re.search(r'(\d+)', line)
            if wc_match:
                try:
                    current_property["bathrooms"] = int(wc_match.group(1))
                except ValueError:
                    pass

        # Square footage - Portuguese patterns like "100m2", "120 m²", etc.
        elif any(pattern in line_lower for pattern in ['m2', 'm²', 'metros']) and current_property:
            sqft_match = re.search(r'(\d{2,4})', line)
            if sqft_match:
                try:
                    current_property["sqft"] = int(sqft_match.group(1))
                except ValueError:
                    pass

        # Long-term rental indicators - prioritize LT over AL (Alojamento Local)
        elif any(pattern in line_lower for pattern in ['arrendamento', 'rental', 'aluguer', 'longa duração', 'permanente', 'residencial']) and current_property:
            if "description" not in current_property:
                current_property["description"] = ""
            current_property["description"] += "[RENTAL] " + line.strip() + " "
            # Mark as rental property
            current_property["listing_type"] = "rental"
        
        # Sale indicators - exclude these properties
        elif any(pattern in line_lower for pattern in ['venda', 'comprar', 'buy', 'sale', 'vender']) and current_property:
            # Skip this property - it's for sale, not rent
            current_property = {}
            continue
        
        # AL (Alojamento Local) indicator - flag but don't exclude automatically
        elif any(pattern in line_lower for pattern in ['alojamento local', 'al ', 'short-term', 'turístico', 'turistico']) and current_property:
            if "description" not in current_property:
                current_property["description"] = ""
            current_property["description"] += "[AL_FLG] " + line.strip() + " "
            # Still mark as rental but note it's short-term
            if "listing_type" not in current_property:
                current_property["listing_type"] = "rental"

        # Furnished indicator - common in Portuguese market
        elif any(pattern in line_lower for pattern in ['mobilado', 'equipped', 'equipada', 'furnished']) and current_property:
            if "description" not in current_property:
                current_property["description"] = ""
            current_property["description"] += "[FURNISHED] " + line.strip() + " "

    # Add final property
    if current_property and "address" in current_property:
        try:
            city = current_property.get("city", "").lower()
            if any(algarve_city in city for algarve_city in algarve_cities):
                listing = PropertyListing(**current_property)
                properties.append(listing)
        except Exception:
            pass

    # Filter by requirements and ensure rentals only
    filtered = []
    for prop in properties:
        # Exclude sale properties - check URL and description
        url_lower = prop.url.lower() if prop.url else ""
        desc_lower = prop.description.lower() if prop.description else ""
        
        # Skip if it's clearly a sale listing
        sale_indicators = ['venda', 'comprar', '/venda/', '/comprar/', 'buy', 'sale']
        if any(indicator in url_lower or indicator in desc_lower for indicator in sale_indicators):
            continue
        
        # Ensure it's a rental - check for rental indicators
        rental_indicators = ['arrendamento', 'aluguer', '/arrendamento/', '/aluguer/', 'rental']
        has_rental_indicator = any(indicator in url_lower or indicator in desc_lower for indicator in rental_indicators)
        
        # If no clear rental indicator, skip it (better to be safe)
        if not has_rental_indicator:
            continue
        
        # Budget filter - for rentals, this is monthly rent
        if requirements.budget_max and prop.price:
            # If budget_max is very high (>50k), likely annual, convert to monthly
            monthly_budget = requirements.budget_max if requirements.budget_max < 50000 else requirements.budget_max // 12
            if prop.price > monthly_budget:
                continue
        
        # Bedrooms filter
        if requirements.bedrooms is not None and prop.bedrooms is not None and prop.bedrooms != requirements.bedrooms:
            continue
        
        # Bathrooms filter
        if requirements.bathrooms and prop.bathrooms and prop.bathrooms < requirements.bathrooms:
            continue
        
        # Add flag if it's likely AL (short-term) vs LT
        if prop.description and ("[AL_FLG]" in prop.description or "alojamento local" in prop.description.lower()):
            # Mark as potential AL but don't exclude - let the user decide
            if prop.description:
                prop.description += " [POTENTIAL_AL_LISTING] "
        
        filtered.append(prop)

    return filtered