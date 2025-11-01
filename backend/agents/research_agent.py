from uagents import Agent, Context
from models import ResearchRequest, ResearchResponse, PropertyListing
from clients.brigthdata import BrightDataClient
import aiohttp, os, json
from bs4 import BeautifulSoup
import re


ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_URL = "https://api.asi1.ai/v1/chat/completions"
BRIGHTDATA_TOKEN = os.getenv("BRIGHT_DATA_API_KEY")


def extract_first_image_from_html(html_content: str) -> str | None:
    """Extract the first property image URL from HTML content."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        img_tags = soup.find_all('img', src=True)
        
        for img in img_tags:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if img_url:
                # Skip small images, icons, and logos
                if any(skip in img_url.lower() for skip in ['icon', 'logo', 'avatar', 'badge', 'button', '16x16', '32x32', '48x48', '64x64']):
                    continue
                # Make absolute URL if relative
                if img_url.startswith('//'):
                    return 'https:' + img_url
                elif img_url.startswith('/'):
                    return None  # Would need base URL
                elif img_url.startswith('http'):
                    return img_url
        return None
    except Exception as e:
        print(f"[HTML Image Extract Error] {e}")
        return None


def extract_first_image_from_markdown(markdown: str) -> str | None:
    """Extract the first image URL from markdown content."""
    import re
    # Look for markdown image syntax: ![alt](url)
    img_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    matches = re.findall(img_pattern, markdown)

    if matches:
        # Filter for likely property images (avoid icons, logos, etc.)
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


async def generate_llm_summary(search_results: list, requirements, original_query: str) -> str:
    """Use ASI-1 to generate a conversational summary from search results."""
    headers = {
        "Authorization": f"Bearer {ASI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Format search results
    results_text = ""
    for i, result in enumerate(search_results[:8], 1):
        title = result.get("title", "")
        description = result.get("description", "")
        link = result.get("link", "")
        results_text += f"{i}. {title}\n"
        if description:
            results_text += f"   {description}\n"
        results_text += f"   Link: {link}\n\n"

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

    body = {
        "model": "asi-1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly Portuguese real estate assistant. Based on search results, "
                    "provide a natural, conversational summary in Portuguese of available properties. "
                    "Mention 2-3 specific listings with addresses and key details. "
                    "Keep it warm and helpful, 3-4 sentences max. "
                    "DO NOT mention the total number of listings in your response. "
                    "Use Portuguese language and Portuguese real estate terminology (quartos, casas de banho, etc.)."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"O utilizador está à procura de: {req_text}\n\n"
                    f"Resultados da pesquisa:\n{results_text}\n"
                    "Resuma que imóveis estão disponíveis. Não mencione quantas listagens há."
                ),
            },
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ASI_URL, headers=headers, json=body) as resp:
                if resp.status != 200:
                    return f"Aqui estão algumas listagens de imóveis em {requirements.location}. Confira os resultados para mais detalhes!"

                res = await resp.json()
                if "choices" in res and res["choices"]:
                    return res["choices"][0]["message"]["content"]
                else:
                    return f"Aqui estão algumas listagens de imóveis em {requirements.location}. Confira os resultados para mais detalhes!"
    except Exception as e:
        ctx_logger = None  # We don't have ctx here, so just print
        print(f"[LLM Summary Error] {e}")
        return f"Aqui estão algumas listagens de imóveis em {requirements.location}. Confira os resultados para mais detalhes!"


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

        # Build search query for Bright Data - Portuguese real estate search
        prompt_parts = [req.location]

        # Add Portugal if not already in location
        if "portugal" not in req.location.lower():
            prompt_parts.append("Portugal")

        if req.bedrooms:
            prompt_parts.append(f"{req.bedrooms} quartos")
        if req.bathrooms:
            prompt_parts.append(f"{req.bathrooms} casas de banho")

        prompt_parts.append("casas à venda")

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

                    # Try to scrape the first 5 results for images
                    results_to_scrape = organic_results[:5]
                    ctx.logger.info(f"Scraping {len(results_to_scrape)} results for images")

                    # Portuguese real estate sites for scraping
                    portuguese_sites = ['idealista.pt', 'imovirtual.com', 'casa.sapo.pt', 'imoovivo.com']
                    
                    for idx, result in enumerate(results_to_scrape):
                        result_url = result.get("link", "")
                        if result_url and any(site in result_url for site in portuguese_sites):
                            ctx.logger.info(f"Scraping result {idx + 1} for images and property data: {result_url}")
                            try:
                                # Try HTML scraping first (if available in Bright Data)
                                scrape_result = await brightdata.call(
                                    "scrape_as_markdown",
                                    {"url": result_url}
                                )
                                if scrape_result["success"]:
                                    markdown = scrape_result.get("output", "")
                                    
                                    # Try to parse properties from HTML (if Bright Data provides HTML, we'd need a different tool)
                                    # For now, extract image from markdown
                                    image_url = extract_first_image_from_markdown(markdown)
                                    
                                    # Also try to get HTML content if available
                                    # Note: Bright Data scrape_as_markdown might contain HTML tags, let's check
                                    if '<html' in markdown.lower() or '<body' in markdown.lower():
                                        # Markdown contains HTML, parse it
                                        html_properties = parse_portuguese_html(markdown, req, result_url)
                                        if html_properties:
                                            # Add parsed properties to our list
                                            for html_prop in html_properties:
                                                if html_prop not in properties:
                                                    properties.append(html_prop)
                                    
                                    if image_url:
                                        ctx.logger.info(f"Found image for result {idx + 1}: {image_url[:100]}")
                                        result_images.append({"index": idx, "image_url": image_url})
                                    else:
                                        ctx.logger.info(f"No image found for result {idx + 1}")
                                else:
                                    ctx.logger.warning(f"Scrape failed for result {idx + 1}")
                            except Exception as e:
                                ctx.logger.warning(f"Failed to scrape result {idx + 1}: {e}")
                        else:
                            ctx.logger.info(f"Skipping result {idx + 1} (not a Portuguese real estate site)")

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
                                longitude=None
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

        # Build summary - use LLM if we have organic results
        total_results = len(organic_results) if organic_results else len(properties)

        if organic_results and len(organic_results) > 0:
            ctx.logger.info("Generating LLM summary from search results")
            summary = await generate_llm_summary(organic_results, req, prompt)

        elif properties:
            summary = f"Aqui estão imóveis em {req.location}"
            if req.bedrooms:
                summary += f" com {req.bedrooms} quartos"
            if req.bathrooms:
                summary += f" e {req.bathrooms} casas de banho"
            if req.budget_max:
                mil = req.budget_max / 1000000
                summary += f" até {mil:.1f}M€"
        else:
            summary = f"Nenhum imóvel encontrado que corresponda aos seus critérios. Tente ajustar os parâmetros de pesquisa."

        # For backwards compatibility, keep top_result_image as the first image
        top_result_image = result_images[0]["image_url"] if result_images else None

        await ctx.send(sender, ResearchResponse(
            properties=properties,
            search_summary=summary,
            total_found=total_results,
            session_id=msg.session_id,
            raw_search_results=organic_results if organic_results else None,
            top_result_image_url=top_result_image,
            result_images=result_images if result_images else None
        ))

    return agent


def parse_portuguese_html(html_content: str, requirements, url: str = "") -> list:
    """Parse HTML from Portuguese real estate sites (Idealista, Imovirtual, etc.) to extract property listings"""
    properties = []
    
    if not html_content:
        return properties
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"[HTML Parse Error] Failed to parse HTML: {e}")
        return properties
    
    # Detect site type from URL or HTML structure
    is_idealista = 'idealista' in url.lower() or soup.find('body', class_=re.compile('idealista', re.I))
    is_imovirtual = 'imovirtual' in url.lower() or soup.find('body', class_=re.compile('imovirtual', re.I))
    is_casa_sapo = 'casa.sapo' in url.lower() or soup.find('body', class_=re.compile('sapo', re.I))
    
    # Extract property listings based on site type
    if is_idealista:
        properties = _parse_idealista_html(soup, url)
    elif is_imovirtual:
        properties = _parse_imovirtual_html(soup, url)
    elif is_casa_sapo:
        properties = _parse_casa_sapo_html(soup, url)
    else:
        # Generic parsing for unknown sites
        properties = _parse_generic_portuguese_html(soup, url)
    
    # Filter by requirements
    filtered = []
    for prop in properties:
        # Filter by budget
        if requirements.budget_max and prop.price and prop.price > requirements.budget_max:
            continue

        # Filter by bedrooms
        if requirements.bedrooms and prop.bedrooms and prop.bedrooms != requirements.bedrooms:
            continue

        # Filter by bathrooms
        if requirements.bathrooms and prop.bathrooms and prop.bathrooms < requirements.bathrooms:
            continue

        filtered.append(prop)

    return filtered


def _parse_idealista_html(soup: BeautifulSoup, base_url: str) -> list:
    """Parse Idealista HTML structure"""
    properties = []
    
    # Idealista structure: property cards are usually in containers with class containing "item"
    property_cards = soup.find_all(['article', 'div'], class_=re.compile(r'item|property|listing|card', re.I))
    
    for card in property_cards:
        prop = {}
        
        # Extract price (usually in span/div with price-related classes)
        price_elem = card.find(['span', 'div', 'p'], class_=re.compile(r'price|preço|valor', re.I))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Extract number from text like "€ 250.000" or "250.000 €"
            price_match = re.search(r'[\d.]+', price_text.replace('.', '').replace(',', '.'))
            if price_match:
                try:
                    prop['price'] = int(float(price_match.group().replace('.', '')))
                except:
                    pass
        
        # Extract address (usually in a link or heading)
        address_elem = card.find(['a', 'h2', 'h3', 'span'], class_=re.compile(r'address|morada|location|title', re.I))
        if not address_elem:
            address_elem = card.find('a', href=re.compile(r'/imovel/|/casa/'))
        
        if address_elem:
            prop['address'] = address_elem.get_text(strip=True)
            if address_elem.name == 'a' and address_elem.get('href'):
                prop['url'] = address_elem.get('href') if address_elem.get('href').startswith('http') else f"https://www.idealista.pt{address_elem.get('href')}"
        
        # Extract bedrooms (quartos)
        quartos_elem = card.find(['span', 'div'], class_=re.compile(r'quartos|bedrooms|bed', re.I))
        if not quartos_elem:
            # Look for text patterns like "3 quartos" or "3 qts"
            quartos_text = card.get_text()
            quartos_match = re.search(r'(\d+)\s*(?:quartos?|qts?|bedrooms?)', quartos_text, re.I)
            if quartos_match:
                try:
                    prop['bedrooms'] = int(quartos_match.group(1))
                except:
                    pass
        else:
            quartos_text = quartos_elem.get_text(strip=True)
            quartos_match = re.search(r'(\d+)', quartos_text)
            if quartos_match:
                try:
                    prop['bedrooms'] = int(quartos_match.group(1))
                except:
                    pass
        
        # Extract bathrooms (casas de banho)
        banhos_elem = card.find(['span', 'div'], class_=re.compile(r'banhos?|bathrooms?|bath', re.I))
        if not banhos_elem:
            banhos_text = card.get_text()
            banhos_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:casas?\s+de\s+banho|banhos?|baths?)', banhos_text, re.I)
            if banhos_match:
                try:
                    prop['bathrooms'] = float(banhos_match.group(1))
                except:
                    pass
        else:
            banhos_text = banhos_elem.get_text(strip=True)
            banhos_match = re.search(r'(\d+(?:\.\d+)?)', banhos_text)
            if banhos_match:
                try:
                    prop['bathrooms'] = float(banhos_match.group(1))
                except:
                    pass
        
        # Extract area (m²)
        area_elem = card.find(['span', 'div'], class_=re.compile(r'area|superficie|m2|metros', re.I))
        if not area_elem:
            area_text = card.get_text()
            area_match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', area_text, re.I)
            if area_match:
                try:
                    # Convert m² to sqft (approximate: 1 m² = 10.764 sqft)
                    sqft = int(float(area_match.group(1)) * 10.764)
                    prop['sqft'] = sqft
                except:
                    pass
        else:
            area_text = area_elem.get_text(strip=True)
            area_match = re.search(r'(\d+(?:\.\d+)?)', area_text)
            if area_match:
                try:
                    sqft = int(float(area_match.group(1)) * 10.764)
                    prop['sqft'] = sqft
                except:
                    pass
        
        # Extract description
        desc_elem = card.find(['p', 'div'], class_=re.compile(r'description|descricao|details', re.I))
        if desc_elem:
            prop['description'] = desc_elem.get_text(strip=True)[:500]  # Limit description length
        
        # Extract city from address
        if 'address' in prop:
            # Portuguese addresses often have format: "Street, City, Region"
            parts = prop['address'].split(',')
            if len(parts) >= 2:
                prop['city'] = parts[-2].strip() if len(parts) > 2 else parts[-1].strip()
        
        # Only add if we have at least address or price
        if prop.get('address') or prop.get('price'):
            try:
                listing = PropertyListing(
                    address=prop.get('address', 'Unknown'),
                    city=prop.get('city', ''),
                    price=prop.get('price'),
                    bedrooms=prop.get('bedrooms'),
                    bathrooms=prop.get('bathrooms'),
                    sqft=prop.get('sqft'),
                    description=prop.get('description'),
                    url=prop.get('url', base_url),
                    latitude=None,
                    longitude=None
                )
                properties.append(listing)
            except Exception as e:
                print(f"[Idealista Parse] Skipping invalid property: {e}")
    
    return properties


def _parse_imovirtual_html(soup: BeautifulSoup, base_url: str) -> list:
    """Parse Imovirtual HTML structure"""
    properties = []
    
    # Imovirtual structure: listings are usually in divs with specific classes
    property_cards = soup.find_all(['article', 'div'], class_=re.compile(r'property|listing|result|item', re.I))
    
    for card in property_cards:
        prop = {}
        
        # Extract price
        price_elem = card.find(['span', 'div', 'strong'], class_=re.compile(r'price|preço', re.I))
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\d.]+', price_text.replace('.', '').replace(',', '.'))
            if price_match:
                try:
                    prop['price'] = int(float(price_match.group().replace('.', '')))
                except:
                    pass
        
        # Extract address/title
        title_elem = card.find(['a', 'h2', 'h3'], class_=re.compile(r'title|name|address', re.I))
        if title_elem:
            prop['address'] = title_elem.get_text(strip=True)
            if title_elem.name == 'a' and title_elem.get('href'):
                prop['url'] = title_elem.get('href') if title_elem.get('href').startswith('http') else f"https://www.imovirtual.com{title_elem.get('href')}"
        
        # Extract features (quartos, banhos, area)
        features_text = card.get_text()
        
        # Quartos
        quartos_match = re.search(r'(\d+)\s*(?:quartos?|qts?)', features_text, re.I)
        if quartos_match:
            try:
                prop['bedrooms'] = int(quartos_match.group(1))
            except:
                pass
        
        # Banhos
        banhos_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:casas?\s+de\s+banho|banhos?)', features_text, re.I)
        if banhos_match:
            try:
                prop['bathrooms'] = float(banhos_match.group(1))
            except:
                pass
        
        # Area
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', features_text, re.I)
        if area_match:
            try:
                sqft = int(float(area_match.group(1)) * 10.764)
                prop['sqft'] = sqft
            except:
                pass
        
        # Extract city
        if 'address' in prop:
            parts = prop['address'].split(',')
            if len(parts) >= 2:
                prop['city'] = parts[-2].strip() if len(parts) > 2 else parts[-1].strip()
        
        if prop.get('address') or prop.get('price'):
            try:
                listing = PropertyListing(
                    address=prop.get('address', 'Unknown'),
                    city=prop.get('city', ''),
                    price=prop.get('price'),
                    bedrooms=prop.get('bedrooms'),
                    bathrooms=prop.get('bathrooms'),
                    sqft=prop.get('sqft'),
                    description=prop.get('description'),
                    url=prop.get('url', base_url),
                    latitude=None,
                    longitude=None
                )
                properties.append(listing)
            except Exception as e:
                print(f"[Imovirtual Parse] Skipping invalid property: {e}")
    
    return properties


def _parse_casa_sapo_html(soup: BeautifulSoup, base_url: str) -> list:
    """Parse Casa Sapo HTML structure"""
    # Similar structure to Idealista/Imovirtual
    return _parse_generic_portuguese_html(soup, base_url)


def _parse_generic_portuguese_html(soup: BeautifulSoup, base_url: str) -> list:
    """Generic parser for Portuguese real estate sites"""
    properties = []
    
    # Look for common patterns across Portuguese sites
    property_cards = soup.find_all(['article', 'div', 'li'], class_=re.compile(r'property|listing|card|item|result', re.I))
    
    for card in property_cards:
        prop = {}
        card_text = card.get_text()
        
        # Price (€ format)
        price_match = re.search(r'€\s*([\d.\s]+)', card_text)
        if price_match:
            try:
                price_str = price_match.group(1).replace('.', '').replace(' ', '')
                prop['price'] = int(float(price_str))
            except:
                pass
        
        # Address (look for Portuguese street patterns)
        address_elem = card.find(['a', 'h2', 'h3'], href=re.compile(r'/imovel|/casa|/apartamento|/moradia'))
        if address_elem:
            prop['address'] = address_elem.get_text(strip=True)
            if address_elem.name == 'a':
                prop['url'] = address_elem.get('href')
        
        # Quartos
        quartos_match = re.search(r'(\d+)\s*(?:quartos?|qts?)', card_text, re.I)
        if quartos_match:
            try:
                prop['bedrooms'] = int(quartos_match.group(1))
            except:
                pass
        
        # Banhos
        banhos_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:casas?\s+de\s+banho|banhos?)', card_text, re.I)
        if banhos_match:
            try:
                prop['bathrooms'] = float(banhos_match.group(1))
            except:
                pass
        
        # Area (m²)
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]', card_text, re.I)
        if area_match:
            try:
                sqft = int(float(area_match.group(1)) * 10.764)
                prop['sqft'] = sqft
            except:
                pass
        
        # Extract city
        if 'address' in prop:
            parts = prop['address'].split(',')
            if len(parts) >= 2:
                prop['city'] = parts[-2].strip() if len(parts) > 2 else parts[-1].strip()
        
        if prop.get('address') or prop.get('price'):
            try:
                listing = PropertyListing(
                    address=prop.get('address', 'Unknown'),
                    city=prop.get('city', ''),
                    price=prop.get('price'),
                    bedrooms=prop.get('bedrooms'),
                    bathrooms=prop.get('bathrooms'),
                    sqft=prop.get('sqft'),
                    description=prop.get('description'),
                    url=prop.get('url', base_url),
                    latitude=None,
                    longitude=None
                )
                properties.append(listing)
            except Exception as e:
                print(f"[Generic Parse] Skipping invalid property: {e}")
    
    return properties