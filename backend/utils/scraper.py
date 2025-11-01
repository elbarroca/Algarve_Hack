"""
Property scraping utilities for Portuguese real estate sites
"""
import re
import json
from typing import Optional, List, Dict
from bs4 import BeautifulSoup


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
        
        # Find all property cards
        property_cards = soup.find_all('div', class_='property')
        
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
            
            # Extract URL from link
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem.get('href')
                # Extract actual URL from tracking URL
                if 'l=' in href:
                    url_match = re.search(r'l=([^&]+)', href)
                    if url_match:
                        prop['url'] = url_match.group(1)
                    else:
                        prop['url'] = href
                else:
                    prop['url'] = href if href.startswith('http') else f"https://casa.sapo.pt{href}"
            
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
        
        return properties
        
    except Exception as e:
        print(f"[Casa Sapo Listing Scrape Error] {e}")
        return []


def filter_rental_properties(properties: List[Dict]) -> List[Dict]:
    """Filter properties to only include rentals."""
    return [p for p in properties if p.get('is_rent', False) or p.get('price_type', '').lower() in ['alugar', 'rent']]


def format_property_json(property_data: Dict) -> Dict:
    """
    Format property data into standardized JSON format.
    """
    return {
        'property_type': property_data.get('property_type', ''),
        'location': {
            'street': property_data.get('street', ''),
            'neighborhood': property_data.get('neighborhood', ''),
            'city': property_data.get('city', ''),
            'district': property_data.get('district', ''),
            'full_address': property_data.get('location', ''),
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

