from uagents import Agent, Context
from models import ResearchRequest, ResearchResponse, PropertyListing, UserRequirements
from typing import Optional
from clients.brigthdata import BrightDataClient
from clients.firecrawl_mcp import get_firecrawl_mcp_client
from utils.scraper import (
    extract_properties_from_casa_sapo_listing,
    filter_rental_properties,
    format_property_json,
    extract_property_from_casa_sapo_html,
)
from utils.firecrawl_scraper import get_firecrawl_scraper
import aiohttp, os, json
import asyncio
import re

ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_URL = "https://api.asi1.ai/v1/chat/completions"
BRIGHTDATA_TOKEN = os.getenv("BRIGHT_DATA_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def filter_results_by_location(search_results: list, required_location: str) -> list:
    """Filter out results that are not real estate listings in the requested location."""
    filtered = []
    location_lower = required_location.lower()

    # Portuguese real estate domains we want to keep
    valid_domains = [
        'idealista.pt', 'idealista.com',
        'imovirtual.com',
        'remax.pt',
        'century21.pt',
        'casa.sapo.pt',
        'imoovivo.com',
        'kyero.com',
        'remax-portugal.com',
        'era.pt',
        'engelvoelkers.com',
        'imovirtual.pt'
    ]

    for result in search_results:
        title = result.get("title", "")
        description = result.get("description", "")
        link = result.get("link", "")

        title_lower = title.lower()
        description_lower = description.lower()
        link_lower = link.lower()

        # First check: Must be from a real estate website
        is_real_estate_site = any(domain in link_lower for domain in valid_domains)

        if not is_real_estate_site:
            print(f"[Location Filter] ❌ Not a real estate site: {title[:80]}")
            continue

        # Second check: Must contain the location
        has_location = location_lower in title_lower or location_lower in description_lower or location_lower in link_lower

        if not has_location:
            print(f"[Location Filter] ❌ Wrong location: {title[:80]}")
            continue

        # Passed both checks
        filtered.append(result)

    print(f"[Location Filter] ✅ Filtered from {len(search_results)} to {len(filtered)} results")
    return filtered


async def generate_llm_summary(properties_or_results, requirements, original_query: str, is_json_properties: bool = False) -> str:
    """
    Generate a conversational summary from either formatted JSON properties or raw search results.
    
    Args:
        properties_or_results: Either List[dict] of formatted JSON properties or List[dict] of raw search results
        requirements: UserRequirements object
        original_query: Original search query
        is_json_properties: True if properties_or_results contains formatted JSON properties, False for raw search results
    """
    headers = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Format properties/results for LLM
    properties_text = ""
    
    if is_json_properties:
        # Handle formatted JSON properties
        formatted_properties = properties_or_results
        for i, prop in enumerate(formatted_properties[:5], 1):  # Limit to 5 for summary
            prop_type = prop.get('property_type', 'Imóvel')
            location = prop.get('location', {})
            address = location.get('full_address', location.get('street', 'Unknown'))
            price_info = prop.get('price', {})
            price_amount = price_info.get('amount', 'N/A')
            bedrooms = prop.get('property_details', {}).get('bedrooms')
            
            properties_text += f"{i}. {prop_type}"
            if bedrooms:
                properties_text += f" com {bedrooms} quartos"
            properties_text += f" em {address}"
            if price_amount and price_amount != 'N/A':
                properties_text += f" - {price_amount}€/mês"
            properties_text += "\n"
    else:
        # Handle raw search results
        search_results = properties_or_results
        for i, result in enumerate(search_results[:8], 1):
            title = result.get("title", "")
            description = result.get("description", "")
            link = result.get("link", "")
            properties_text += f"{i}. {title}\n"
            if description:
                properties_text += f"   {description}\n"
            properties_text += f"   Link: {link}\n\n"

    # Build requirement summary in Portuguese
    req_parts = [requirements.location]
    if requirements.bedrooms:
        req_parts.append(f"{requirements.bedrooms} quartos")
    if requirements.bathrooms:
        req_parts.append(f"{requirements.bathrooms} casas de banho")
    if requirements.budget_max:
        mil = requirements.budget_max / 1000000
        req_parts.append(f"orçamento até {mil:.1f}M€")
    req_text = ", ".join(req_parts)

    # Determine the input label based on type
    input_label = "Propriedades encontradas" if is_json_properties else "Resultados da pesquisa"
    
    body = {
        "model": "asi-1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly Portuguese real estate assistant. Based on rental property listings, "
                    "provide a natural, conversational summary in Portuguese of available properties to rent. "
                    "Mention 2-3 specific listings with addresses and key details. "
                    "Keep it warm and helpful, 3-4 sentences max. "
                    "Emphasize these are RENTAL properties (para alugar). "
                    "DO NOT mention the total number of listings in your response. "
                    "Use Portuguese language and Portuguese real estate terminology (quartos, casas de banho, etc.)."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"O utilizador está à procura de imóveis para ALUGAR: {req_text}\n\n"
                    f"{input_label}:\n{properties_text}\n"
                    "Resuma que imóveis estão disponíveis para alugar. Não mencione quantas listagens há."
                ),
            },
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ASI_URL, headers=headers, json=body) as resp:
                if resp.status != 200:
                    count = len(properties_or_results)
                    return f"Encontrei {count} imóveis para alugar em {requirements.location}. Confira os resultados para mais detalhes!"

                res = await resp.json()
                if "choices" in res and res["choices"]:
                    return res["choices"][0]["message"]["content"]
                else:
                    count = len(properties_or_results)
                    return f"Encontrei {count} imóveis para alugar em {requirements.location}. Confira os resultados para mais detalhes!"
    except Exception as e:
        print(f"[LLM Summary Error] {e}")
        count = len(properties_or_results)
        return f"Encontrei {count} imóveis para alugar em {requirements.location}. Confira os resultados para mais detalhes!"


async def decide_tool(prompt: str) -> dict:
    """Ask ASI-1 which MCP tool to use. Returns fallback plan on error."""
    headers = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "asi-1-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a planning model for Bright Data MCP. "
                    "Given a user query, output JSON {tool:'', arguments:{}} only."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ASI_URL, headers=headers, json=body) as resp:
            status = resp.status
            try:
                res = await resp.json()
            except Exception:
                text = await resp.text()
                return {"tool": "search_engine", "arguments": {"query": prompt}, "error": f"Bad JSON: {text}"}

    # 🔎 Debug: if API returned an error, log and fall back
    if "choices" not in res:
        print(f"[ASI-1 ERROR] status={status}, response={res}")
        return {"tool": "search_engine", "arguments": {"query": prompt}, "error": res.get("error", res)}

    # ✅ Extract output safely
    raw = res["choices"][0]["message"]["content"]
    try:
        return json.loads(raw)
    except Exception:
        return {"tool": "search_engine", "arguments": {"query": prompt}}

async def scrape_listing_page(
    result: dict,
    idx: int,
    firecrawl_mcp,
    firecrawl,
    brightdata,
    req,
    portuguese_sites: list,
    semaphore: asyncio.Semaphore,
    ctx: Context
) -> dict:
    """
    Async function to scrape a listing page and extract properties.
    Returns dict with listing_properties and result_url or None if failed.
    """
    result_url = result.get("link", "")
    if not result_url or not any(site in result_url for site in portuguese_sites):
        return None
    
    async with semaphore:  # Limit concurrent requests
        try:
            ctx.logger.info(f"Scraping listing page {idx + 1}: {result_url}")
            
            html_content = None
            
            # Try Firecrawl MCP first if available
            if firecrawl_mcp:
                try:
                    firecrawl_result = await firecrawl_mcp.scrape(result_url, formats=["html", "markdown"])
                    if firecrawl_result:
                        html_content = firecrawl_result.get("html", "")
                        ctx.logger.info(f"✅ Firecrawl MCP scraped listing: {result_url}")
                except Exception as e:
                    ctx.logger.debug(f"Firecrawl MCP failed, trying Firecrawl SDK: {e}")
            
            # Try Firecrawl Python SDK if MCP didn't work
            if not html_content and firecrawl:
                try:
                    firecrawl_result = await firecrawl.scrape_property_page(result_url)
                    if firecrawl_result:
                        html_content = firecrawl_result.get("html", "")
                        ctx.logger.info(f"✅ Firecrawl SDK scraped listing: {result_url}")
                except Exception as e:
                    ctx.logger.debug(f"Firecrawl SDK failed, trying Bright Data: {e}")
            
            # Fallback to Bright Data if Firecrawl didn't work
            if not html_content:
                try:
                    scrape_result = await brightdata.call(
                        "scrape_as_markdown",
                        {"url": result_url}
                    )
                    if scrape_result["success"]:
                        markdown = scrape_result.get("output", "")
                        # Check if markdown contains HTML
                        if '<html' in markdown.lower() or '<body' in markdown.lower() or '<div' in markdown.lower():
                            html_content = markdown
                    
                    # Also try HTML scraping
                    if not html_content:
                        scrape_result = await brightdata.call(
                            "scrape_as_html",
                            {"url": result_url}
                        )
                        if scrape_result["success"]:
                            html_content = scrape_result.get("output", "")
                except Exception as e:
                    ctx.logger.warning(f"Bright Data scrape failed: {e}")
            
            # Parse properties from HTML
            if html_content:
                # Check if this is a Casa Sapo listing page
                if 'casa.sapo.pt' in result_url:
                    # Extract properties from listing page using utils
                    listing_properties = extract_properties_from_casa_sapo_listing(html_content, result_url)
                    return {
                        "listing_properties": listing_properties,
                        "result_url": result_url
                    }
                else:
                    # For non-Casa Sapo sites, log and skip
                    ctx.logger.info(f"Skipping non-Casa Sapo site: {result_url}")
            
            return None
        except Exception as e:
            ctx.logger.warning(f"Failed to scrape listing page {idx + 1}: {e}")
            return None


async def scrape_property_details(
    prop_data: dict,
    firecrawl_mcp,
    firecrawl,
    brightdata,
    req,
    semaphore: asyncio.Semaphore,
    ctx: Context
) -> dict:
    """
    Async function to scrape a single property's details.
    Returns formatted property dict or None if failed.
    """
    prop_url = prop_data.get('url', '')
    if not prop_url:
        return None
    
    async with semaphore:  # Limit concurrent requests
        try:
            ctx.logger.info(f"  → Scraping individual property: {prop_url}")
            
            detail_html = None
            
            # Try Firecrawl MCP for detail page
            if firecrawl_mcp:
                try:
                    detail_result = await firecrawl_mcp.scrape(prop_url, formats=["html", "markdown"])
                    if detail_result:
                        detail_html = detail_result.get("html", "")
                except Exception as e:
                    ctx.logger.debug(f"Firecrawl MCP detail scrape failed: {e}")
            
            # Try Firecrawl SDK if MCP didn't work
            if not detail_html and firecrawl:
                try:
                    detail_result = await firecrawl.scrape_property_page(prop_url)
                    if detail_result:
                        detail_html = detail_result.get("html", "")
                except Exception as e:
                    ctx.logger.debug(f"Firecrawl SDK detail scrape failed: {e}")
            
            # Fallback to Bright Data
            if not detail_html:
                try:
                    detail_scrape = await brightdata.call(
                        "scrape_as_markdown",
                        {"url": prop_url}
                    )
                    if detail_scrape["success"]:
                        detail_html = detail_scrape.get("output", "")
                except:
                    pass
            
            # Extract full property details using utils
            if detail_html and 'casa.sapo.pt' in prop_url:
                full_prop_data = extract_property_from_casa_sapo_html(detail_html, prop_url)
                if full_prop_data:
                    # Merge with listing data
                    prop_data.update(full_prop_data)
            
            # Format as JSON using utils
            formatted_prop = format_property_json(prop_data)
            
            ctx.logger.info(f"✅ Formatted rental property JSON: {formatted_prop.get('property_type', 'Unknown')} - {formatted_prop.get('location', {}).get('full_address', 'Unknown')} - {formatted_prop.get('price', {}).get('amount', 'N/A')}€")
            
            return {
                "formatted_prop": formatted_prop,
                "prop_data": prop_data,
                "prop_url": prop_url
            }
        except Exception as e:
            ctx.logger.warning(f"Failed to scrape property {prop_url}: {e}")
            return None


def score_property_match(prop_data: dict, requirements) -> float:
    """
    Score a property based on how well it matches the user's requirements.
    Returns a score from 0.0 to 100.0 (higher = better match).
    """
    score = 0.0
    
    # Extract property details - handle both raw and formatted structures
    price_amount = None
    if 'price' in prop_data:
        if isinstance(prop_data['price'], dict):
            # Formatted structure: {'price': {'amount': 1250, ...}}
            price_amount = prop_data['price'].get('amount')
        else:
            # Raw structure: {'price': 1250}
            price_amount = prop_data['price']
    
    if isinstance(price_amount, str):
        # Extract numeric value from strings like "1250€"
        try:
            price_amount = float(''.join(filter(str.isdigit, str(price_amount))))
        except:
            price_amount = None
    
    bedrooms = None
    if 'property_details' in prop_data and isinstance(prop_data.get('property_details'), dict):
        bedrooms = prop_data['property_details'].get('bedrooms')
    if not bedrooms:
        bedrooms = prop_data.get('bedrooms')
    
    bathrooms = None
    if 'property_details' in prop_data and isinstance(prop_data.get('property_details'), dict):
        bathrooms = prop_data['property_details'].get('bathrooms')
    if not bathrooms:
        bathrooms = prop_data.get('bathrooms')
    
    location = prop_data.get('location', {})
    if isinstance(location, dict):
        address = location.get('full_address', '') or location.get('street', '')
    else:
        address = str(location) if location else ''
    
    # 1. Bedrooms match (40 points max)
    if requirements.bedrooms and bedrooms:
        if bedrooms == requirements.bedrooms:
            score += 40.0  # Exact match
        elif bedrooms == requirements.bedrooms + 1:
            score += 35.0  # Close match (+1)
        elif bedrooms == requirements.bedrooms - 1:
            score += 30.0  # Close match (-1)
        elif bedrooms >= requirements.bedrooms:
            score += 20.0  # More bedrooms (acceptable)
        else:
            score += 10.0  # Fewer bedrooms (less ideal)
    elif requirements.bedrooms:
        # Missing bedroom info - penalize
        score -= 10.0
    
    # 2. Budget match (35 points max)
    if requirements.budget_max and price_amount:
        # Convert budget_max from annual to monthly if needed (typical rental budgets are monthly)
        # Check if budget_max seems like annual (large number) or monthly (smaller number)
        budget_monthly = requirements.budget_max
        if requirements.budget_max > 10000:  # Likely annual budget
            budget_monthly = requirements.budget_max / 12
        
        if price_amount <= budget_monthly:
            # Within budget - calculate how close to max
            ratio = price_amount / budget_monthly
            if ratio <= 0.7:
                score += 35.0  # Well within budget (great value)
            elif ratio <= 0.85:
                score += 30.0  # Good budget match
            elif ratio <= 0.95:
                score += 25.0  # Close to budget
            else:
                score += 20.0  # At budget limit
        else:
            # Over budget - penalize based on how much over
            overage_ratio = (price_amount - budget_monthly) / budget_monthly
            if overage_ratio <= 0.1:
                score += 10.0  # Slightly over (10% overage)
            elif overage_ratio <= 0.2:
                score += 5.0   # Moderately over (20% overage)
            else:
                score -= 20.0  # Way over budget
    elif requirements.budget_max:
        # Missing price info - penalize
        score -= 15.0
    
    # 3. Location relevance (15 points max)
    if requirements.location and address:
        location_lower = requirements.location.lower()
        address_lower = address.lower()
        if location_lower in address_lower:
            score += 15.0  # Exact location match
        elif any(word in address_lower for word in location_lower.split()):
            score += 10.0  # Partial location match
        else:
            score += 5.0   # Different location
    
    # 4. Bathrooms match (10 points max)
    if requirements.bathrooms and bathrooms:
        if bathrooms == requirements.bathrooms:
            score += 10.0
        elif bathrooms >= requirements.bathrooms:
            score += 8.0
        else:
            score += 5.0
    
    # 5. Property completeness bonus (5 points max)
    completeness_bonus = 0.0
    if prop_data.get('description'):
        completeness_bonus += 1.0
    images = prop_data.get('images', [])
    if images and len(images) > 0:
        completeness_bonus += 2.0
    # Check coordinates - can be at root or in location dict
    if prop_data.get('latitude') and prop_data.get('longitude'):
        completeness_bonus += 2.0
    elif isinstance(location, dict):
        if location.get('latitude') and location.get('longitude'):
            completeness_bonus += 2.0
    score += completeness_bonus
    
    # Ensure score is between 0 and 100
    return max(0.0, min(100.0, score))


def calculate_negotiation_score(prop_data: dict, requirements: Optional[UserRequirements] = None) -> float:
    """
    Calculate negotiation score (0-10) based on factors that indicate negotiation potential.
    Higher score = more negotiation leverage for the buyer.
    
    Factors considered:
    - Price relative to budget (lower price = higher leverage)
    - Description keywords indicating seller motivation
    - Property condition indicators
    - Price per square meter (if available)
    - Missing information (indicates potential issues)
    """
    score = 5.0  # Base score (neutral)
    
    # Extract price
    price_amount = None
    if 'price' in prop_data:
        if isinstance(prop_data['price'], dict):
            price_amount = prop_data['price'].get('amount')
        else:
            price_amount = prop_data['price']
    
    if isinstance(price_amount, str):
        try:
            price_amount = float(''.join(filter(str.isdigit, str(price_amount))))
        except:
            price_amount = None
    
    # Extract description
    description = prop_data.get('description', '') or prop_data.get('details', '') or ''
    desc_lower = description.lower()
    
    # Factor 1: Price relative to budget (if budget available)
    if requirements and requirements.budget_max and price_amount:
        # Convert budget_max from annual to monthly if needed
        budget_monthly = requirements.budget_max
        if requirements.budget_max > 10000:
            budget_monthly = requirements.budget_max / 12
        
        if price_amount > 0:
            price_ratio = price_amount / budget_monthly if budget_monthly > 0 else 1.0
            
            # Lower price relative to budget = more negotiation room
            if price_ratio < 0.6:
                score += 1.5  # Well below budget - seller might be flexible
            elif price_ratio < 0.8:
                score += 1.0  # Below budget - some negotiation room
            elif price_ratio > 1.2:
                score -= 0.5  # Over budget - seller might be firm
    
    # Factor 2: Description keywords indicating seller motivation or issues
    motivation_keywords = [
        'as-is', 'as is', 'needs renovation', 'needs work', 'fixer upper',
        'motivated seller', 'must sell', 'quick sale', 'reduced', 'price drop',
        'foreclosure', 'bank owned', 'estate sale', 'divorce', 'relocation',
        'vacant', 'empty', 'unoccupied', 'distressed', 'below market'
    ]
    
    for keyword in motivation_keywords:
        if keyword in desc_lower:
            score += 0.8  # Strong indicator of negotiation potential
            break
    
    # Factor 3: Property condition indicators
    condition_keywords = [
        'needs repair', 'needs maintenance', 'handyman special', 'fixer',
        'cosmetic updates', 'updating needed', 'original condition',
        'dated', 'outdated', 'old', 'needs updating'
    ]
    
    for keyword in condition_keywords:
        if keyword in desc_lower:
            score += 0.5
            break
    
    # Factor 4: Price per square meter (if available)
    sqft = prop_data.get('sqft') or prop_data.get('sqft_living') or prop_data.get('square_feet')
    if price_amount and sqft and sqft > 0:
        price_per_sqm = price_amount / (sqft / 10.764)  # Convert sqft to m²
        # Very low price per sqm might indicate negotiation potential
        if price_per_sqm < 500:  # Adjust threshold based on market
            score += 0.5
    
    # Factor 5: Missing information (indicates potential issues)
    missing_fields = 0
    if not prop_data.get('bedrooms'):
        missing_fields += 1
    if not prop_data.get('bathrooms'):
        missing_fields += 1
    if not prop_data.get('sqft') and not prop_data.get('sqft_living'):
        missing_fields += 1
    if not description or len(description) < 50:
        missing_fields += 1
    
    if missing_fields >= 3:
        score += 0.5  # Missing info might indicate motivated seller
    
    # Factor 6: Negative description indicators
    negative_keywords = [
        'no photos', 'photo coming soon', 'see agent remarks',
        'call for details', 'contact agent', 'needs inspection'
    ]
    
    for keyword in negative_keywords:
        if keyword in desc_lower:
            score += 0.3
            break
    
    # Factor 7: Long time on market indicators (if we can detect)
    if 'days on market' in desc_lower or 'dom' in desc_lower:
        score += 0.5
    
    # Ensure score is between 0 and 10
    return round(max(0.0, min(10.0, score)), 1)


def create_research_agent(port: int = 8002):
    agent = Agent(
        name="research_agent",
        port=port,
        seed="research_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    brightdata = BrightDataClient()

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Research Agent started at {ctx.agent.address}")

    @agent.on_message(model=ResearchRequest)
    async def handle_request(ctx: Context, sender: str, msg: ResearchRequest):
        req = msg.requirements

        # Build search query for Bright Data - Portuguese real estate search (RENTALS ONLY)
        prompt_parts = [req.location]

        # Add Portugal if not already in location
        if "portugal" not in req.location.lower():
            prompt_parts.append("Portugal")

        if req.bedrooms:
            prompt_parts.append(f"{req.bedrooms} quartos")
        if req.bathrooms:
            prompt_parts.append(f"{req.bathrooms} casas de banho")

        # Search for RENTALS (alugar) instead of sales
        prompt_parts.append("alugar")
        prompt_parts.append("apartamentos casas")

        if req.budget_max and req.budget_max < 1000000:
            prompt_parts.append(f"até {req.budget_max//1000}k€")
        elif req.budget_max:
            mil = req.budget_max / 1000000
            prompt_parts.append(f"até {mil:.1f}M€")

        prompt = " ".join(prompt_parts)

        ctx.logger.info(f"Search query: {prompt}")

        # Call Bright Data MCP with search_engine tool
        result = await brightdata.call("search_engine", {"query": prompt, "engine": "google"})

        if not result["success"]:
            await ctx.send(sender, ResearchResponse(
                properties=[],
                search_summary=f"Search failed: {result.get('error', 'Unknown error')}",
                total_found=0,
                session_id=msg.session_id
            ))
            return

        # Parse the response to extract property listings
        raw_output = result.get("output", "")
        ctx.logger.info(f"Raw Bright Data output: {raw_output[:500]}...")

        properties = []
        organic_results = []
        result_images = []  # Store images for all results

        try:
            # Try to parse as JSON first
            data = json.loads(raw_output)

            # Handle different response formats
            if isinstance(data, dict):
                # Search engine results format
                if "organic" in data:
                    organic_results = data.get("organic", [])

                    # Check if Bright Data returned empty results
                    if not organic_results or len(organic_results) == 0:
                        ctx.logger.warning("Bright Data returned no organic results")
                        await ctx.send(sender, ResearchResponse(
                            properties=[],
                            search_summary=f"Não conseguimos encontrar imóveis que correspondam aos seus critérios em {req.location}. Tente ajustar o orçamento, número de quartos ou procurar numa área próxima.",
                            total_found=0,
                            session_id=msg.session_id,
                            raw_search_results=[],
                            top_result_image_url=None,
                            result_images=[]
                        ))
                        return

                    ctx.logger.info(f"Found {len(organic_results)} organic search results")

                    # Scrape ALL filtered results to extract full property details
                    results_to_scrape = organic_results  # Scrape all filtered results
                    ctx.logger.info(f"Scraping {len(results_to_scrape)} results for full property data (rentals only)")
                    
                    # Initialize Firecrawl scraper if available (Python SDK)
                    firecrawl = get_firecrawl_scraper()
                    firecrawl_mcp = get_firecrawl_mcp_client()
                    
                    if firecrawl:
                        ctx.logger.info("Using Firecrawl Python SDK for enhanced scraping")
                    elif firecrawl_mcp:
                        ctx.logger.info("Using Firecrawl MCP for enhanced scraping")
                    
                    # Portuguese real estate sites for scraping
                    portuguese_sites = ['idealista.pt', 'imovirtual.com', 'casa.sapo.pt', 'imoovivo.com', 'supercasa.pt']
                    
                    scraped_properties_data = []  # Store raw property data - defined outside loop
                    
                    # Create semaphore for listing page scraping (increase from 5 to 8 for faster processing)
                    listing_semaphore = asyncio.Semaphore(8)
                    
                    # Scrape all listing pages in parallel
                    ctx.logger.info(f"Scraping {len(results_to_scrape)} listing pages in parallel...")
                    listing_tasks = [
                        scrape_listing_page(
                            result,
                            idx,
                            firecrawl_mcp,
                            firecrawl,
                            brightdata,
                            req,
                            portuguese_sites,
                            listing_semaphore,
                            ctx
                        )
                        for idx, result in enumerate(results_to_scrape)
                    ]
                    
                    # Execute all listing page scraping tasks in parallel
                    listing_results = await asyncio.gather(*listing_tasks, return_exceptions=True)
                    
                    # Collect all rental properties from all listing pages
                    all_rental_properties = []
                    for result in listing_results:
                        if isinstance(result, Exception):
                            ctx.logger.warning(f"Listing page scrape task failed: {result}")
                            continue
                        
                        if result and result.get("listing_properties"):
                            listing_properties = result["listing_properties"]
                            # Filter for rentals only using utils
                            rental_properties = filter_rental_properties(listing_properties)
                            all_rental_properties.extend(rental_properties)
                            ctx.logger.info(f"Found {len(listing_properties)} properties, {len(rental_properties)} rentals from {result['result_url']}")
                    
                    ctx.logger.info(f"Total rental properties collected: {len(all_rental_properties)}")
                    
                    if all_rental_properties:
                        # Limit to reasonable number before scraping (to avoid scraping too many)
                        # Reduce from 50 to 30 for faster processing
                        max_properties_to_scrape = min(len(all_rental_properties), 10)  # Scrape up to 30, then filter to top 20
                        properties_to_scrape = all_rental_properties[:max_properties_to_scrape]
                        
                        ctx.logger.info(f"Scraping {len(properties_to_scrape)} rental properties in parallel (will filter to top 20 best matches)...")
                        
                        # Create semaphore to limit concurrent requests (increase from 10 to 15 for faster processing)
                        property_semaphore = asyncio.Semaphore(15)
                        
                        # Create tasks for parallel scraping
                        scrape_tasks = [
                            scrape_property_details(
                                prop_data.copy(),  # Copy to avoid mutating original
                                firecrawl_mcp,
                                firecrawl,
                                brightdata,
                                req,
                                property_semaphore,
                                ctx
                            )
                            for prop_data in properties_to_scrape
                        ]
                        
                        # Execute all scraping tasks in parallel
                        scrape_results = await asyncio.gather(*scrape_tasks, return_exceptions=True)
                        
                        # Process results and score them
                        scored_properties = []
                        for result in scrape_results:
                            if isinstance(result, Exception):
                                ctx.logger.warning(f"Scraping task failed: {result}")
                                continue
                            
                            if result:
                                formatted_prop = result["formatted_prop"]
                                prop_data = result["prop_data"]
                                
                                # Score the property based on requirements match
                                score = score_property_match(prop_data, req)
                                
                                scored_properties.append({
                                    "score": score,
                                    "formatted_prop": formatted_prop,
                                    "prop_data": prop_data,
                                    "prop_url": result["prop_url"]
                                })
                        
                        # Sort by score (highest first) and take top 20
                        scored_properties.sort(key=lambda x: x["score"], reverse=True)
                        top_properties = scored_properties[:20]
                        
                        ctx.logger.info(f"✅ Scored {len(scored_properties)} properties, selected top {len(top_properties)} best matches")
                        if top_properties:
                            ctx.logger.info(f"Score range: {top_properties[-1]['score']:.1f} - {top_properties[0]['score']:.1f}")
                        
                        # Process top properties
                        for item in top_properties:
                            formatted_prop = item["formatted_prop"]
                            prop_data = item["prop_data"]
                            prop_url = item["prop_url"]
                            score = item["score"]
                            
                            scraped_properties_data.append(formatted_prop)
                            
                            # Create PropertyListing for compatibility
                            try:
                                listing = PropertyListing(
                                    address=prop_data.get('location', prop_data.get('street', '')),
                                    city=prop_data.get('city', req.location),
                                    price=prop_data.get('price'),
                                    bedrooms=prop_data.get('bedrooms'),
                                    bathrooms=prop_data.get('bathrooms'),
                                    sqft=prop_data.get('sqft'),
                                    description=prop_data.get('description', ''),
                                    url=prop_url,
                                    latitude=prop_data.get('latitude'),
                                    longitude=prop_data.get('longitude'),
                                    negotiation_score=calculate_negotiation_score(prop_data, req),
                                    # Contact information
                                    contact_phone=prop_data.get('seller_phone') or (prop_data.get('seller', {}).get('phone') if isinstance(prop_data.get('seller'), dict) else None),
                                    contact_email=prop_data.get('seller_email') or (prop_data.get('seller', {}).get('email') if isinstance(prop_data.get('seller'), dict) else None),
                                    seller_name=prop_data.get('seller_name') or (prop_data.get('seller', {}).get('name') if isinstance(prop_data.get('seller'), dict) else None),
                                    seller_url=prop_data.get('seller_url') or (prop_data.get('seller', {}).get('url') if isinstance(prop_data.get('seller'), dict) else None),
                                    # Images
                                    image_url=prop_data.get('image_url') or (prop_data.get('images', [None])[0] if isinstance(prop_data.get('images'), list) and prop_data.get('images') else None),
                                    images=prop_data.get('images') if isinstance(prop_data.get('images'), list) else ([prop_data.get('image_url')] if prop_data.get('image_url') else None),
                                    # Additional details
                                    property_type=prop_data.get('property_type'),
                                    price_type=prop_data.get('price_type'),
                                    original_price=prop_data.get('original_price')
                                )
                                properties.append(listing)
                                ctx.logger.info(f"✅ Added rental property (score: {score:.1f}): {prop_data.get('location', 'Unknown')} - {prop_data.get('price', 'N/A')}€")
                            except Exception as e:
                                ctx.logger.warning(f"Failed to create PropertyListing: {e}")
                        
                        ctx.logger.info(f"✅ Completed parallel scraping: {len(scraped_properties_data)} top properties processed")
                    
                    # Log summary after all scraping is done
                    if scraped_properties_data:
                        ctx.logger.info(f"📊 Scraped {len(scraped_properties_data)} rental properties with full details")

                # Direct property listings format (if available)
                if "properties" in data:
                    for prop_data in data.get("properties", []):
                        try:
                            listing = PropertyListing(
                                address=prop_data.get("address", "Unknown"),
                                city=prop_data.get("city", req.location),
                                price=prop_data.get("price"),
                                bedrooms=prop_data.get("bedrooms"),
                                bathrooms=prop_data.get("bathrooms"),
                                sqft=prop_data.get("sqft"),
                                description=prop_data.get("description"),
                                url=prop_data.get("url"),
                                latitude=None,
                                longitude=None,
                                negotiation_score=calculate_negotiation_score(prop_data, req),
                                # Contact information
                                contact_phone=prop_data.get('seller_phone') or (prop_data.get('seller', {}).get('phone') if isinstance(prop_data.get('seller'), dict) else None),
                                contact_email=prop_data.get('seller_email') or (prop_data.get('seller', {}).get('email') if isinstance(prop_data.get('seller'), dict) else None),
                                seller_name=prop_data.get('seller_name') or (prop_data.get('seller', {}).get('name') if isinstance(prop_data.get('seller'), dict) else None),
                                seller_url=prop_data.get('seller_url') or (prop_data.get('seller', {}).get('url') if isinstance(prop_data.get('seller'), dict) else None),
                                # Images
                                image_url=prop_data.get('image_url') or (prop_data.get('images', [None])[0] if isinstance(prop_data.get('images'), list) and prop_data.get('images') else None),
                                images=prop_data.get('images') if isinstance(prop_data.get('images'), list) else ([prop_data.get('image_url')] if prop_data.get('image_url') else None),
                                # Additional details
                                property_type=prop_data.get('property_type'),
                                price_type=prop_data.get('price_type'),
                                original_price=prop_data.get('original_price')
                            )
                            properties.append(listing)
                        except Exception as e:
                            ctx.logger.warning(f"Skipping invalid property: {e}")

        except json.JSONDecodeError:
            ctx.logger.warning("Could not parse response as JSON")

        # Filter organic results by location BEFORE processing
        if organic_results and len(organic_results) > 0:
            ctx.logger.info(f"Filtering {len(organic_results)} results by location: {req.location}")
            organic_results = filter_results_by_location(organic_results, req.location)
            ctx.logger.info(f"After filtering: {len(organic_results)} results remain")

            # Check if filtering removed all results
            if not organic_results or len(organic_results) == 0:
                ctx.logger.warning(f"All results filtered out - no properties in {req.location}")
                await ctx.send(sender, ResearchResponse(
                    properties=[],
                    search_summary=f"Não conseguimos encontrar imóveis que correspondam aos seus critérios em {req.location}. A pesquisa retornou resultados de outras áreas, mas nenhum especificamente em {req.location}. Tente expandir a sua pesquisa para cidades próximas ou ajustar os seus critérios.",
                    total_found=0,
                    session_id=msg.session_id,
                    raw_search_results=[],
                    top_result_image_url=None,
                    result_images=[]
                ))
                return

        # If we don't have parsed properties from HTML scraping, create PropertyListing objects from organic search results
        if len(properties) == 0 and organic_results and len(organic_results) > 0:
            ctx.logger.info(f"Creating PropertyListing objects from {len(organic_results)} organic search results")
            for idx, result in enumerate(organic_results):
                try:
                    # Extract basic info from search result
                    title = result.get("title", "")
                    description = result.get("description", "")
                    link = result.get("link", "")
                    
                    # Try to extract price from title or description
                    price = None
                    price_text = (title + " " + description).lower()
                    price_match = re.search(r'([\d.]+)\s*(?:k|mil|m|milh[ao]es?)?\s*€', price_text)
                    if price_match:
                        try:
                            num_str = price_match.group(1).replace('.', '')
                            if 'mil' in price_text or 'k' in price_text:
                                price = int(float(num_str) * 1000)
                            elif 'm' in price_text or 'milh' in price_text:
                                price = int(float(num_str) * 1000000)
                            else:
                                price = int(float(num_str))
                        except:
                            pass
                    
                    # Try to extract bedrooms
                    bedrooms = None
                    bed_match = re.search(r'(\d+)\s*(?:quartos?|qts?|bedrooms?)', title + " " + description, re.I)
                    if bed_match:
                        try:
                            bedrooms = int(bed_match.group(1))
                        except:
                            pass
                    
                    # Extract address from title (usually format: "Property description, Street, City")
                    address = title
                    city = req.location
                    if ',' in title:
                        parts = title.split(',')
                        address = parts[0].strip()
                        if len(parts) > 1:
                            city = parts[-1].strip()
                    
                    # Create PropertyListing
                    # Prepare prop_data dict for negotiation score calculation
                    prop_data_dict = {
                        'price': price,
                        'bedrooms': bedrooms if bedrooms else req.bedrooms,
                        'bathrooms': None,
                        'sqft': None,
                        'description': description[:500] if description else None,
                        'address': address
                    }
                    listing = PropertyListing(
                        address=address,
                        city=city,
                        price=price,
                        bedrooms=bedrooms if bedrooms else req.bedrooms,
                        bathrooms=None,
                        sqft=None,
                        description=description[:500] if description else None,
                        url=link,
                        latitude=None,
                        longitude=None,
                        negotiation_score=calculate_negotiation_score(prop_data_dict, req),
                        # Contact information - not available from organic search
                        contact_phone=None,
                        contact_email=None,
                        seller_name=None,
                        seller_url=None,
                        # Images - not available from organic search
                        image_url=None,
                        images=None,
                        # Additional details
                        property_type=None,
                        price_type=None,
                        original_price=None
                    )
                    properties.append(listing)
                    ctx.logger.info(f"✅ Created PropertyListing from search result {idx + 1}: {address[:50]}")
                except Exception as e:
                    ctx.logger.warning(f"Failed to create PropertyListing from search result {idx + 1}: {e}")

        # Build summary - use LLM if we have organic results
        total_results = len(scraped_properties_data) if scraped_properties_data else (len(organic_results) if organic_results else len(properties))

        if scraped_properties_data and len(scraped_properties_data) > 0:
            # Use LLM to generate summary from formatted JSON properties
            ctx.logger.info(f"Generating LLM summary from {len(scraped_properties_data)} rental properties")
            summary = await generate_llm_summary(scraped_properties_data, req, prompt, is_json_properties=True)
        elif organic_results and len(organic_results) > 0:
            ctx.logger.info("Generating LLM summary from search results")
            summary = await generate_llm_summary(organic_results, req, prompt, is_json_properties=False)
        elif properties:
            summary = f"Encontrei {len(properties)} imóveis para alugar em {req.location}"
            if req.bedrooms:
                summary += f" com {req.bedrooms} quartos"
            if req.bathrooms:
                summary += f" e {req.bathrooms} casas de banho"
            if req.budget_max:
                mil = req.budget_max / 1000000
                summary += f" até {mil:.1f}M€"
        else:
            summary = f"Nenhum imóvel para alugar encontrado que corresponda aos seus critérios. Tente ajustar os parâmetros de pesquisa."

        # For backwards compatibility, keep top_result_image as the first image
        top_result_image = None
        if scraped_properties_data and len(scraped_properties_data) > 0:
            first_prop_images = scraped_properties_data[0].get('images', [])
            top_result_image = first_prop_images[0] if first_prop_images else None
        elif result_images:
            top_result_image = result_images[0]["image_url"] if result_images else None

        ctx.logger.info(f"📊 Final summary: {len(scraped_properties_data) if scraped_properties_data else len(properties)} rental properties, {len(scraped_properties_data)} with full JSON details")

        await ctx.send(sender, ResearchResponse(
            properties=properties,
            search_summary=summary,
            total_found=total_results,
            session_id=msg.session_id,
            raw_search_results=organic_results if organic_results else None,
            top_result_image_url=top_result_image,
            result_images=result_images if result_images else None,
            formatted_properties_json=scraped_properties_data if scraped_properties_data else None
        ))

    return agent
