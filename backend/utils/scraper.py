"""
Property scraping utilities for Portuguese real estate sites
"""
import re
import json
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin


def is_individual_listing_url(url: str) -> bool:
    """
    Validate if a URL points to an individual property listing (not a search/feed page).
    Returns True if it's an individual listing, False if it's a feed/search page.
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Feed/search page patterns (should be excluded)
    # BUT: Idealista individual URLs can have /arrendar-casas/ in them, so we need to be careful
    feed_patterns = [
        '/search', '/list', '/results', '/pesquisa', '/listings',
        '/venda-', '/aluguer-',  # Search category pages
        '/for-sale', '/for-rent', '/to-rent' , '/rent/'
    ]
    
    # Idealista-specific: check if it's a search/feed page (has query params or ends with /)
    # Individual Idealista URLs: /arrendar-casas/faro/apartamento-123456.html or /imovel/123456.html
    # Feed pages: /arrendar-casas/faro/ or /arrendar-casas/faro/?ordenado-por=preco-asc
    is_idealista_feed = False
    if 'idealista.pt' in url_lower:
        # Feed pages usually end with / or have query params without a property ID
        if url_lower.endswith('/') or (url_lower.count('/') <= 4 and '?' in url_lower):
            # Check if it has a property ID pattern
            if not re.search(r'-\d{6,}\.html|/imovel/\d+|/apartamento-\d+|/moradia-\d+|/casa-\d+', url_lower):
                is_idealista_feed = True
    
    # Check other feed patterns (but exclude Idealista URLs that might have /arrendar- in path)
    is_feed = False
    if not is_idealista_feed:
        is_feed = any(pattern in url_lower for pattern in feed_patterns)
        # Also check for search pages that aren't Idealista
        if '/comprar-' in url_lower and 'idealista.pt' not in url_lower:
            is_feed = True
        if '/alugar-' in url_lower and 'idealista.pt' not in url_lower:
            is_feed = True
        if '/arrendar-' in url_lower and 'idealista.pt' not in url_lower:
            is_feed = True
    
    # Individual listing patterns (should be included)
    individual_patterns = [
        r'/imovel/[^/]+[-/]\d+',  # Casa Sapo: /imovel/apartamento-faro-123456
        r'/imovel/\d+',  # Idealista: /imovel/123456.html
        r'/imoveis/[^/]+[-/]\d+',  # General: /imoveis/apartamento-123456
        r'/detail/\d+',  # /detail/123456
        r'/property/\d+',  # /property/123456
        r'/anuncio/\d+',  # ImOvirtual: /anuncio/123456
        r'/anuncio/[^/]+-\d+',  # ImOvirtual: /anuncio/apartamento-t2-faro-123456
        r'-\d{6,}\.html',  # Idealista: /arrendar-casas/faro/apartamento-123456.html
        r'/imovel-\d+',  # Idealista: /imovel-123456
        r'/apartamento-\d+',  # /apartamento-123456-faro.html
        r'/moradia-\d+',  # /moradia-123456-algarve.html
        r'/apartamento/\d+',  # /apartamento/123456
        r'/moradia/\d+',  # /moradia/123456
        r'/casa/\d+',  # /casa/123456
        r'/casa-\d+',  # /casa-123456.html
        r'[-/]ID\d+',  # /property-ID123456
        # Idealista pattern: /arrendar-casas/{city}/{property-type}-{id}.html
        r'/arrendar-casas/[^/]+/[^/]+-\d{6,}\.html',  # /arrendar-casas/faro/apartamento-123456.html
        r'/comprar-casas/[^/]+/[^/]+-\d{6,}\.html',  # /comprar-casas/faro/apartamento-123456.html
    ]
    
    # Check if it matches individual listing patterns
    is_individual = any(re.search(pattern, url_lower) for pattern in individual_patterns)
    
    # If it has query parameters (? in URL), it's likely a search page unless it's clearly an individual listing
    has_query_params = '?' in url and not is_individual
    
    # Return True only if it's clearly an individual listing and not a feed page
    return is_individual and not (is_feed or has_query_params or is_idealista_feed)


def extract_individual_property_url_from_card(card_element, base_url: str = '') -> Optional[str]:
    """
    Extract the individual property detail page URL from a property card element.
    Handles different real estate site structures (Casa Sapo, Idealista, ImOvirtual, etc.)
    """
    if not card_element:
        return None

    # Try to find the main property link
    # Usually the property card has a primary link to the detail page
    link_elem = None

    # Try different link selection strategies (ordered by specificity)
    strategies = [
        # Casa Sapo specific
        ('a', {'class': re.compile(r'propertyCardStyled__Link', re.I)}),
        ('a', {'class': re.compile(r'searchPropertyCard__container', re.I)}),
        ('a', {'href': re.compile(r'/imovel/[^/]+-\d+', re.I)}),  # Casa Sapo individual listings
        # Idealista specific
        ('a', {'class': re.compile(r'item-link', re.I)}),
        # General patterns
        ('a', {'class': re.compile(r'property.*link|detail.*link|card.*link', re.I)}),
        ('a', {'href': re.compile(r'/(imovel|property|detail|anuncio|apartamento|moradia|casa)/', re.I)}),
        ('a', {'href': True}),  # Fallback: any link
    ]

    for tag, attrs in strategies:
        # Find all links matching the strategy
        link_elems = card_element.find_all(tag, attrs, limit=5)  # Check multiple links

        for link_elem in link_elems:
            href = link_elem.get('href', '')

            if not href:
                continue

            # Handle tracking URLs (extract actual URL)
            if 'l=' in href or 'url=' in href:
                # Extract from tracking parameter
                url_match = re.search(r'[?&](?:l|url)=([^&]+)', href)
                if url_match:
                    try:
                        href = unquote(url_match.group(1))
                    except:
                        pass

            # Build full URL
            if href.startswith('http'):
                full_url = href
            elif href.startswith('/'):
                # Use base_url domain
                if base_url:
                    domain_match = re.match(r'(https?://[^/]+)', base_url)
                    if domain_match:
                        full_url = domain_match.group(1) + href
                    else:
                        full_url = href
                else:
                    full_url = href
            else:
                full_url = urljoin(base_url, href) if base_url else href

            # Validate it's an individual listing
            if is_individual_listing_url(full_url):
                return full_url

    return None


def extract_property_from_casa_sapo_html(html_content: str, url: str) -> Optional[Dict]:
    """
    Extract property data from Casa Sapo HTML.
    Handles both listing pages and individual property detail pages.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find JSON-LD structured data first (most reliable)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        property_data = {}
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Offer':
                    # Extract from JSON-LD
                    property_data['name'] = data.get('name', '')
                    property_data['category'] = data.get('category', '')
                    
                    # Price
                    price_str = data.get('price', [''])[0] if isinstance(data.get('price'), list) else str(data.get('price', ''))
                    if price_str:
                        price_match = re.search(r'([\d.]+)', price_str.replace('.', '').replace(',', '.'))
                        if price_match:
                            try:
                                property_data['price'] = int(float(price_match.group(1).replace('.', '')))
                            except:
                                pass
                    
                    # Location from availableAtOrFrom
                    if 'availableAtOrFrom' in data:
                        location = data['availableAtOrFrom']
                        if 'address' in location:
                            addr = location['address']
                            property_data['city'] = addr.get('addressLocality', '')
                            property_data['region'] = addr.get('addressRegion', '')
                            property_data['country'] = addr.get('addressCountry', '')
                        
                        # Coordinates
                        if 'geo' in location:
                            geo = location['geo']
                            property_data['latitude'] = geo.get('latitude')
                            property_data['longitude'] = geo.get('longitude')
                    
                    # Seller info
                    if 'seller' in data:
                        seller = data['seller']
                        property_data['seller_name'] = seller.get('name', '')
                        property_data['seller_phone'] = seller.get('telephone', '')
                        property_data['seller_url'] = seller.get('url', '')
                        
                        if 'address' in seller:
                            seller_addr = seller['address']
                            if isinstance(seller_addr, dict) and 'streetAddress' in seller_addr:
                                property_data['seller_address'] = seller_addr['streetAddress']
                    
                    # Image
                    property_data['image_url'] = data.get('image', '')
                    break
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Extract from HTML if JSON-LD didn't provide everything
        # Property type
        if 'category' not in property_data:
            type_elem = soup.find('div', class_='property-type')
            if type_elem:
                property_data['property_type'] = type_elem.get_text(strip=True)
        
        # Location
        if 'city' not in property_data:
            location_elem = soup.find('div', class_='property-location')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                property_data['location'] = location_text
                # Parse location: "Street, Neighborhood, City, District"
                parts = [p.strip() for p in location_text.split(',')]
                if len(parts) >= 2:
                    property_data['street'] = parts[0]
                    property_data['neighborhood'] = parts[1] if len(parts) > 2 else ''
                    property_data['city'] = parts[-2] if len(parts) > 2 else parts[-1]
                    property_data['district'] = parts[-1] if len(parts) > 2 else ''
        
        # Price and rent/sale type
        price_elem = soup.find('div', class_='property-price')
        if price_elem:
            price_type_elem = price_elem.find('div', class_='property-price-type')
            if price_type_elem:
                price_type = price_type_elem.get_text(strip=True).lower()
                property_data['is_rent'] = 'alugar' in price_type or 'rent' in price_type
                property_data['price_type'] = price_type
            
            price_value_elem = price_elem.find('div', class_='property-price-value')
            if price_value_elem:
                price_text = price_value_elem.get_text(strip=True)
                # Extract price (handle reductions)
                price_match = re.search(r'([\d.]+)', price_text.replace('.', '').replace(',', '.'))
                if price_match:
                    try:
                        property_data['price'] = int(float(price_match.group(1).replace('.', '')))
                    except:
                        pass
                
                # Check for price reduction
                reduction_elem = price_value_elem.find('span', class_='price-reduction')
                if reduction_elem:
                    reduction_value_elem = reduction_elem.find('span', class_='price-reduction-value')
                    if reduction_value_elem:
                        old_price_text = reduction_value_elem.get_text(strip=True)
                        old_price_match = re.search(r'([\d.]+)', old_price_text.replace('.', '').replace(',', '.'))
                        if old_price_match:
                            try:
                                property_data['original_price'] = int(float(old_price_match.group(1).replace('.', '')))
                            except:
                                pass
        
        # Extract all images
        images = []
        picture_tags = soup.find_all('picture', class_='property-photos')
        for picture in picture_tags:
            # Try source tags first (webp)
            sources = picture.find_all('source')
            for source in sources:
                srcset = source.get('srcset', '')
                if srcset:
                    # Extract highest resolution image
                    img_urls = [url.strip().split()[0] for url in srcset.split(',')]
                    if img_urls:
                        images.append(img_urls[-1])  # Highest resolution
            
            # Fallback to img tag
            img_tag = picture.find('img')
            if img_tag:
                img_src = img_tag.get('src') or img_tag.get('data-src')
                if img_src and img_src not in images:
                    images.append(img_src)
        
        if images:
            property_data['images'] = images
            property_data['image_url'] = images[0]  # Primary image
        
        # Extract bedrooms from property type (T1, T2, T3, etc.)
        if 'property_type' in property_data:
            type_text = property_data['property_type']
            bed_match = re.search(r'T(\d+)', type_text, re.I)
            if bed_match:
                try:
                    property_data['bedrooms'] = int(bed_match.group(1))
                except:
                    pass
        
        # URL
        property_data['url'] = url
        
        # Description (if available)
        desc_elem = soup.find(['div', 'section'], class_=re.compile(r'description|descricao|details', re.I))
        if desc_elem:
            property_data['description'] = desc_elem.get_text(strip=True)[:1000]
        
        return property_data if property_data else None
        
    except Exception as e:
        print(f"[Casa Sapo Scrape Error] {e}")
        return None


def extract_properties_from_casa_sapo_listing(html_content: str, base_url: str) -> List[Dict]:
    """
    Extract multiple properties from a Casa Sapo listing page.
    Returns list of property dictionaries.
    """
    properties = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all property cards - try multiple selectors
        property_cards = (
            soup.find_all('div', class_='property') or
            soup.find_all('div', class_=re.compile(r'propertyCard|searchPropertyCard', re.I)) or
            soup.find_all('article', class_=re.compile(r'property', re.I)) or
            soup.find_all('div', {'data-testid': re.compile(r'property', re.I)})
        )
        
        for card in property_cards:
            prop = {}
            
            # Extract property type
            type_elem = card.find('div', class_='property-type')
            if type_elem:
                prop['property_type'] = type_elem.get_text(strip=True)
                
                # Extract bedrooms from type (T1, T2, etc.)
                type_text = prop['property_type']
                bed_match = re.search(r'T(\d+)', type_text, re.I)
                if bed_match:
                    try:
                        prop['bedrooms'] = int(bed_match.group(1))
                    except:
                        pass
            
            # Extract location
            location_elem = card.find('div', class_='property-location')
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                prop['location'] = location_text
                parts = [p.strip() for p in location_text.split(',')]
                if len(parts) >= 2:
                    prop['street'] = parts[0]
                    prop['neighborhood'] = parts[1] if len(parts) > 2 else ''
                    prop['city'] = parts[-2] if len(parts) > 2 else parts[-1]
                    prop['district'] = parts[-1] if len(parts) > 2 else ''
            
            # Extract price and rent/sale type
            price_elem = card.find('div', class_='property-price')
            if price_elem:
                price_type_elem = price_elem.find('div', class_='property-price-type')
                if price_type_elem:
                    price_type = price_type_elem.get_text(strip=True).lower()
                    prop['is_rent'] = 'alugar' in price_type or 'rent' in price_type
                    prop['price_type'] = price_type
                
                price_value_elem = price_elem.find('div', class_='property-price-value')
                if price_value_elem:
                    price_text = price_value_elem.get_text(strip=True)
                    price_match = re.search(r'([\d.]+)', price_text.replace('.', '').replace(',', '.'))
                    if price_match:
                        try:
                            prop['price'] = int(float(price_match.group(1).replace('.', '')))
                        except:
                            pass
            
            # Extract image URL
            picture = card.find('picture', class_='property-photos')
            if picture:
                img_tag = picture.find('img')
                if img_tag:
                    prop['image_url'] = img_tag.get('src') or img_tag.get('data-src')
                    # Try to get higher resolution from source
                    sources = picture.find_all('source')
                    if sources:
                        last_source = sources[-1]
                        srcset = last_source.get('srcset', '')
                        if srcset:
                            img_urls = [url.strip().split()[0] for url in srcset.split(',')]
                            if img_urls:
                                prop['image_url'] = img_urls[-1]
            
            # Extract individual property detail page URL (not feed URL)
            individual_url = extract_individual_property_url_from_card(card, base_url)
            if individual_url:
                prop['url'] = individual_url
                print(f"[Scraper] ✅ Found individual listing: {individual_url[:80]}")
            else:
                # If we can't find a valid individual URL, skip this card
                print(f"[Scraper] ⚠️ No valid individual URL found in property card")
                continue
            
            # Extract JSON-LD data if available
            json_ld_script = card.find('script', type='application/ld+json')
            if json_ld_script:
                try:
                    json_data = json.loads(json_ld_script.string)
                    if json_data.get('@type') == 'Offer':
                        # Get coordinates
                        if 'availableAtOrFrom' in json_data and 'geo' in json_data['availableAtOrFrom']:
                            geo = json_data['availableAtOrFrom']['geo']
                            prop['latitude'] = geo.get('latitude')
                            prop['longitude'] = geo.get('longitude')
                        
                        # Get seller info
                        if 'seller' in json_data:
                            seller = json_data['seller']
                            prop['seller_name'] = seller.get('name', '')
                            prop['seller_phone'] = seller.get('telephone', '')
                except:
                    pass
            
            if prop:
                properties.append(prop)
        
        # FALLBACK: If no property cards found, extract individual property URLs from all links on the page
        if not properties:
            print(f"[Casa Sapo Scraper] No property cards found, trying fallback: extracting individual property URLs from links...")
            all_links = soup.find_all('a', href=True)
            seen_urls = set()
            
            for link in all_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    # Casa Sapo URLs
                    if 'casa.sapo.pt' in base_url:
                        full_url = 'https://casa.sapo.pt' + href
                    else:
                        continue
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Check if this is an individual property listing URL
                if is_individual_listing_url(full_url) and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # Try to extract basic info from the link text or nearby elements
                    prop = {
                        'url': full_url,
                        'is_rent': '/alugar' in full_url or '/aluguer' in full_url,
                    }
                    
                    # Extract info from link text
                    link_text = link.get_text(strip=True)
                    if link_text:
                        # Try to extract bedrooms from link text
                        bed_match = re.search(r'T(\d+)|(\d+)\s*quartos?', link_text, re.I)
                        if bed_match:
                            try:
                                prop['bedrooms'] = int(bed_match.group(1) or bed_match.group(2))
                            except:
                                pass
                        
                        # Try to extract price from link text
                        price_match = re.search(r'([\d.]+)\s*€|€\s*([\d.]+)', link_text.replace('.', ''))
                        if price_match:
                            try:
                                prop['price'] = int(price_match.group(1) or price_match.group(2))
                            except:
                                pass
                    
                    properties.append(prop)
                    print(f"[Casa Sapo Scraper] ✅ Fallback extracted property URL: {full_url[:80]}")
            
            print(f"[Casa Sapo Scraper] Fallback found {len(properties)} individual property URLs")
        
        return properties
        
    except Exception as e:
        print(f"[Casa Sapo Listing Scrape Error] {e}")
        return []


def extract_properties_from_idealista_listing(html_content: str, base_url: str) -> List[Dict]:
    """
    Extract multiple properties from an Idealista listing page.
    Returns list of property dictionaries with individual listing URLs.
    """
    properties = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract location from listing URL (e.g., "faro" or "faro-distrito" from URL)
        # Example URLs:
        # - https://www.idealista.pt/arrendar-casas/faro-distrito/...
        # - https://www.idealista.pt/arrendar-casas/faro/...
        city_from_url = None
        district_from_url = None
        if base_url:
            # Match pattern like /faro-distrito/ or /faro/
            location_match = re.search(r'/(?:arrendar|comprar)-[^/]+/([^/]+)', base_url)
            if location_match:
                location_part = location_match.group(1)
                # Clean up the location (remove query params, normalize)
                location_clean = location_part.split('?')[0].split('#')[0]

                if '-distrito' in location_clean:
                    # e.g., "faro-distrito" -> district="Faro", city="Faro"
                    district_name = location_clean.replace('-distrito', '').capitalize()
                    district_from_url = district_name
                    city_from_url = district_name  # Use district name as city fallback
                else:
                    # e.g., "faro" -> city="Faro"
                    city_from_url = location_clean.capitalize()

        # Idealista uses article tags with class 'item'
        property_cards = soup.find_all('article', class_=re.compile(r'item'))
        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all('div', class_=re.compile(r'item-info-container'))

        print(f"[Idealista Scraper] Found {len(property_cards)} property cards")
        if city_from_url or district_from_url:
            print(f"[Idealista Scraper] Extracted location from URL: city={city_from_url}, district={district_from_url}")

        for card in property_cards:
            prop = {}
            
            # Extract individual property URL first (most important)
            individual_url = extract_individual_property_url_from_card(card, base_url)
            if not individual_url:
                continue
            
            prop['url'] = individual_url
            
            # Extract property type and bedrooms
            type_elem = card.find(['span', 'p'], class_=re.compile(r'item-detail', re.I))
            if type_elem:
                type_text = type_elem.get_text(strip=True)
                prop['property_type'] = type_text
                
                # Extract bedrooms (T1, T2, etc. or "2 quartos")
                bed_match = re.search(r'T(\d+)|(\d+)\s*quartos?', type_text, re.I)
                if bed_match:
                    try:
                        prop['bedrooms'] = int(bed_match.group(1) or bed_match.group(2))
                    except:
                        pass
            
            # Extract price
            price_elem = card.find(['span', 'div'], class_=re.compile(r'item-price|price', re.I))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'([\d.]+)', price_text.replace('.', ''))
                if price_match:
                    try:
                        prop['price'] = int(price_match.group(1))
                        # Determine if it's rental or sale based on URL or price text
                        if '/alugar' in individual_url or '/arrendar' in individual_url or '/aluguer' in individual_url:
                            prop['is_rent'] = True
                            prop['price_type'] = 'alugar'
                    except:
                        pass
            
            # Extract location
            location_elem = card.find(['p', 'span'], class_=re.compile(r'item-link|location', re.I))
            if location_elem:
                prop['location'] = location_elem.get_text(strip=True)
            
            # Extract image
            img_elem = card.find('img')
            if img_elem:
                prop['image_url'] = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-ondemand-img')

            # Add city and district from URL to improve geocoding accuracy
            if city_from_url:
                prop['city'] = city_from_url
            if district_from_url:
                prop['district'] = district_from_url

            if prop.get('url'):
                properties.append(prop)
                print(f"[Idealista Scraper] ✅ Extracted property: {prop.get('location', 'Unknown')} - {prop.get('url', '')[:80]}")
        
        # FALLBACK: If no property cards found, extract individual property URLs from all links on the page
        if not properties:
            print(f"[Idealista Scraper] No property cards found, trying fallback: extracting individual property URLs from links...")
            all_links = soup.find_all('a', href=True)
            seen_urls = set()
            
            for link in all_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    # Idealista URLs
                    if 'idealista.pt' in base_url:
                        full_url = 'https://www.idealista.pt' + href
                    else:
                        continue
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Check if this is an individual property listing URL
                if is_individual_listing_url(full_url) and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # Try to extract basic info from the link text or nearby elements
                    prop = {
                        'url': full_url,
                        'is_rent': '/arrendar' in full_url or '/alugar' in full_url,
                    }
                    
                    # Extract info from link text
                    link_text = link.get_text(strip=True)
                    if link_text:
                        # Try to extract bedrooms from link text
                        bed_match = re.search(r'T(\d+)|(\d+)\s*quartos?', link_text, re.I)
                        if bed_match:
                            try:
                                prop['bedrooms'] = int(bed_match.group(1) or bed_match.group(2))
                            except:
                                pass
                        
                        # Try to extract price from link text
                        price_match = re.search(r'([\d.]+)\s*€|€\s*([\d.]+)', link_text.replace('.', ''))
                        if price_match:
                            try:
                                prop['price'] = int(price_match.group(1) or price_match.group(2))
                            except:
                                pass
                    
                    # Add city and district from URL
                    if city_from_url:
                        prop['city'] = city_from_url
                    if district_from_url:
                        prop['district'] = district_from_url
                    
                    properties.append(prop)
                    print(f"[Idealista Scraper] ✅ Fallback extracted property URL: {full_url[:80]}")
            
            print(f"[Idealista Scraper] Fallback found {len(properties)} individual property URLs")
        
        return properties
        
    except Exception as e:
        print(f"[Idealista Scraper Error] {e}")
        return []


def extract_properties_from_generic_listing(html_content: str, base_url: str) -> List[Dict]:
    """
    Generic property extraction for unknown Portuguese real estate sites.
    Attempts to find property cards and extract individual listing URLs.
    """
    properties = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try common property card selectors
        card_selectors = [
            {'name': 'div', 'class': re.compile(r'property|listing|item|card', re.I)},
            {'name': 'article', 'class': re.compile(r'property|listing|item', re.I)},
            {'name': 'li', 'class': re.compile(r'property|listing|item', re.I)},
        ]
        
        property_cards = []
        for selector in card_selectors:
            cards = soup.find_all(selector['name'], selector['class'])
            if cards and len(cards) > 0:
                property_cards = cards
                print(f"[Generic Scraper] Found {len(cards)} cards using {selector}")
                break
        
        for card in property_cards:
            # Extract individual URL
            individual_url = extract_individual_property_url_from_card(card, base_url)
            if individual_url:
                prop = {'url': individual_url}
                
                # Try to extract basic info
                # Price
                price_elem = card.find(text=re.compile(r'€|EUR', re.I))
                if price_elem:
                    price_text = str(price_elem)
                    price_match = re.search(r'([\d.]+)', price_text.replace('.', ''))
                    if price_match:
                        try:
                            prop['price'] = int(price_match.group(1))
                        except:
                            pass
                
                # Image
                img_elem = card.find('img')
                if img_elem:
                    prop['image_url'] = img_elem.get('src') or img_elem.get('data-src')
                
                properties.append(prop)
                print(f"[Generic Scraper] ✅ Extracted property URL: {individual_url[:80]}")
        
        # FALLBACK: If no property cards found, extract individual property URLs from all links on the page
        if not properties:
            print(f"[Generic Scraper] No property cards found, trying fallback: extracting individual property URLs from links...")
            all_links = soup.find_all('a', href=True)
            seen_urls = set()
            
            # Determine base domain for relative URLs
            base_domain = ''
            if 'imovirtual.com' in base_url:
                base_domain = 'https://www.imovirtual.com'
            elif 'remax.pt' in base_url:
                base_domain = 'https://www.remax.pt'
            elif 'century21.pt' in base_url:
                base_domain = 'https://www.century21.pt'
            elif 'supercasa.pt' in base_url:
                base_domain = 'https://www.supercasa.pt'
            else:
                # Try to extract from base_url
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    base_domain = f"{parsed.scheme}://{parsed.netloc}"
                except:
                    pass
            
            for link in all_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    if base_domain:
                        full_url = base_domain + href
                    else:
                        continue
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Check if this is an individual property listing URL
                if is_individual_listing_url(full_url) and full_url not in seen_urls:
                    seen_urls.add(full_url)
                    
                    # Try to extract basic info from the link text
                    prop = {
                        'url': full_url,
                        'is_rent': '/alugar' in full_url or '/arrendar' in full_url or '/aluguer' in full_url,
                    }
                    
                    # Extract info from link text
                    link_text = link.get_text(strip=True)
                    if link_text:
                        # Try to extract bedrooms from link text
                        bed_match = re.search(r'T(\d+)|(\d+)\s*quartos?', link_text, re.I)
                        if bed_match:
                            try:
                                prop['bedrooms'] = int(bed_match.group(1) or bed_match.group(2))
                            except:
                                pass
                        
                        # Try to extract price from link text
                        price_match = re.search(r'([\d.]+)\s*€|€\s*([\d.]+)', link_text.replace('.', ''))
                        if price_match:
                            try:
                                prop['price'] = int(price_match.group(1) or price_match.group(2))
                            except:
                                pass
                    
                    properties.append(prop)
                    print(f"[Generic Scraper] ✅ Fallback extracted property URL: {full_url[:80]}")
            
            print(f"[Generic Scraper] Fallback found {len(properties)} individual property URLs")
        
        return properties
        
    except Exception as e:
        print(f"[Generic Scraper Error] {e}")
        return []


def filter_rental_properties(properties: List[Dict]) -> List[Dict]:
    """Filter properties to only include rentals."""
    # More permissive filter - include properties that:
    # 1. Have is_rent=True explicitly set
    # 2. Have price_type indicating rental
    # 3. Have price data (indicating they're real listings, not just search results)
    return [p for p in properties if (
        p.get('is_rent', False) or 
        p.get('price_type', '').lower() in ['alugar', 'rent'] or
        (p.get('price') and p.get('price') > 0)  # Has valid price data
    )]


def format_property_json(property_data: Dict) -> Dict:
    """
    Format property data into standardized JSON format.
    """
    # Construct full_address from actual address components instead of raw 'location' field
    # This ensures proper geocoding (raw 'location' often contains search result titles)
    address_parts = []
    if property_data.get('street'):
        address_parts.append(property_data.get('street'))
    if property_data.get('neighborhood'):
        address_parts.append(property_data.get('neighborhood'))
    if property_data.get('city'):
        address_parts.append(property_data.get('city'))
    if property_data.get('district'):
        address_parts.append(property_data.get('district'))

    # Use constructed address if components available, otherwise fallback to raw location
    full_address = ', '.join(address_parts) if address_parts else property_data.get('location', '')

    return {
        'property_type': property_data.get('property_type', ''),
        'location': {
            'street': property_data.get('street', ''),
            'neighborhood': property_data.get('neighborhood', ''),
            'city': property_data.get('city', ''),
            'district': property_data.get('district', ''),
            'full_address': full_address,
            'latitude': property_data.get('latitude'),
            'longitude': property_data.get('longitude'),
        },
        'price': {
            'amount': property_data.get('price'),
            'currency': 'EUR',
            'type': property_data.get('price_type', ''),  # 'alugar' or 'comprar'
            'is_rent': property_data.get('is_rent', False),
            'original_price': property_data.get('original_price'),
        },
        'property_details': {
            'bedrooms': property_data.get('bedrooms'),
            'bathrooms': property_data.get('bathrooms'),
            'sqft': property_data.get('sqft'),
            'area_m2': property_data.get('area_m2'),
        },
        'images': property_data.get('images', [property_data.get('image_url')] if property_data.get('image_url') else []),
        'description': property_data.get('description', ''),
        'url': property_data.get('url', ''),
        'seller': {
            'name': property_data.get('seller_name', ''),
            'phone': property_data.get('seller_phone', ''),
            'url': property_data.get('seller_url', ''),
            'address': property_data.get('seller_address', ''),
        },
    }


