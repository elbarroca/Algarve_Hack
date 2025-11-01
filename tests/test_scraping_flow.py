"""
Test the complete scraping flow: Feed → Individual Listing URLs → Property Details

This test validates:
1. Feed page scraping extracts individual listing URLs (NOT feed URLs)
2. Individual listing URLs are properly validated
3. Property details can be extracted from individual pages
"""

import sys
import os
import asyncio

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.scraper import (
    extract_properties_from_casa_sapo_listing,
    extract_properties_from_idealista_listing,
    extract_properties_from_generic_listing,
    is_individual_listing_url,
    extract_property_from_casa_sapo_html,
)


# Mock HTML for testing (simplified versions)
MOCK_CASA_SAPO_FEED_HTML = """
<html>
<body>
    <div class="property">
        <div class="property-type">Apartamento T1</div>
        <div class="property-location">Faro, Algarve</div>
        <div class="property-price">420 €/mês</div>
        <picture class="property-photos">
            <img src="https://example.com/image1.jpg" />
        </picture>
        <a href="/imovel/apartamento-t1-faro-123456">Ver detalhes</a>
    </div>
    <div class="property">
        <div class="property-type">Apartamento T2</div>
        <div class="property-location">Faro Centro</div>
        <div class="property-price">550 €/mês</div>
        <picture class="property-photos">
            <img src="https://example.com/image2.jpg" />
        </picture>
        <a href="/imovel/apartamento-t2-faro-789012">Ver detalhes</a>
    </div>
    <div class="property">
        <div class="property-type">Moradia T3</div>
        <div class="property-location">Quarteira</div>
        <div class="property-price">850 €/mês</div>
        <picture class="property-photos">
            <img src="https://example.com/image3.jpg" />
        </picture>
        <!-- THIS SHOULD BE REJECTED - it's a feed page link -->
        <a href="/search?city=faro&type=apartment">Ver mais resultados</a>
    </div>
</body>
</html>
"""

MOCK_IDEALISTA_FEED_HTML = """
<html>
<body>
    <article class="item">
        <span class="item-detail">Apartamento T1</span>
        <p class="item-link">Faro, Centro</p>
        <span class="item-price">450 €/mês</span>
        <img src="https://example.com/idealista1.jpg" />
        <a href="/imovel/123456.html">Ver detalhes</a>
    </article>
    <article class="item">
        <span class="item-detail">Apartamento T2</span>
        <p class="item-link">Faro, São Pedro</p>
        <span class="item-price">600 €/mês</span>
        <img src="https://example.com/idealista2.jpg" />
        <a href="/apartamento-789012-faro.html">Ver detalhes</a>
    </article>
    <article class="item">
        <span class="item-detail">Moradia T3</span>
        <p class="item-link">Quarteira</p>
        <span class="item-price">900 €/mês</span>
        <img src="https://example.com/idealista3.jpg" />
        <!-- THIS SHOULD BE REJECTED - it's a search page link -->
        <a href="/alugar-casas/faro?bedrooms=3">Ver mais</a>
    </article>
</body>
</html>
"""

MOCK_INDIVIDUAL_PROPERTY_HTML = """
<html>
<head>
    <script type="application/ld+json">
    {
        "@type": "Offer",
        "name": "Apartamento T1 em Faro",
        "category": "Apartamento",
        "price": ["420"],
        "availableAtOrFrom": {
            "address": {
                "streetAddress": "Rua Professor António Pinheiro, 8000-243",
                "addressLocality": "Faro",
                "addressRegion": "Algarve"
            }
        }
    }
    </script>
</head>
<body>
    <h1>Apartamento T1 em Faro Centro</h1>
    <div class="price">420 €/mês</div>
    <div class="description">
        Apartamento T1 para alugar em excelente localização no centro de Faro.
        Totalmente renovado, com cozinha equipada.
    </div>
    <div class="details">
        <span>1 quarto</span>
        <span>1 casa de banho</span>
        <span>65 m²</span>
    </div>
</body>
</html>
"""


def test_feed_extraction_casa_sapo():
    """Test extracting individual listing URLs from Casa Sapo feed page."""
    print("=" * 80)
    print("TEST 1: Casa Sapo Feed Extraction")
    print("=" * 80)
    
    base_url = "https://casa.sapo.pt/search?location=faro"
    properties = extract_properties_from_casa_sapo_listing(MOCK_CASA_SAPO_FEED_HTML, base_url)
    
    print(f"\n📊 Extracted {len(properties)} properties from feed")
    
    valid_count = 0
    invalid_count = 0
    
    for i, prop in enumerate(properties, 1):
        prop_url = prop.get('url', '')
        is_valid = is_individual_listing_url(prop_url)
        
        status = "✅" if is_valid else "❌"
        print(f"\n  {status} Property {i}:")
        print(f"     Type: {prop.get('property_type', 'N/A')}")
        print(f"     Location: {prop.get('location', 'N/A')}")
        print(f"     Price: {prop.get('price', 'N/A')}€")
        print(f"     URL: {prop_url}")
        
        if is_valid:
            valid_count += 1
            if '/imovel/' not in prop_url:
                print(f"     ⚠️  WARNING: URL doesn't match expected pattern")
        else:
            invalid_count += 1
            print(f"     ❌ ERROR: This is a feed/search URL, should be rejected!")
    
    print(f"\n📈 Results: {valid_count} valid, {invalid_count} invalid")
    
    # Assert we extracted only individual listings
    assert len(properties) >= 2, "Should extract at least 2 properties"
    assert all(is_individual_listing_url(p.get('url', '')) for p in properties), \
        "All extracted URLs must be individual listings, not feed pages!"
    
    print("\n✅ Test PASSED: All extracted URLs are individual listings\n")


def test_feed_extraction_idealista():
    """Test extracting individual listing URLs from Idealista feed page."""
    print("=" * 80)
    print("TEST 2: Idealista Feed Extraction")
    print("=" * 80)
    
    base_url = "https://www.idealista.pt/alugar-casas/faro"
    properties = extract_properties_from_idealista_listing(MOCK_IDEALISTA_FEED_HTML, base_url)
    
    print(f"\n📊 Extracted {len(properties)} properties from feed")
    
    valid_count = 0
    invalid_count = 0
    
    for i, prop in enumerate(properties, 1):
        prop_url = prop.get('url', '')
        is_valid = is_individual_listing_url(prop_url)
        
        status = "✅" if is_valid else "❌"
        print(f"\n  {status} Property {i}:")
        print(f"     Type: {prop.get('property_type', 'N/A')}")
        print(f"     Location: {prop.get('location', 'N/A')}")
        print(f"     Price: {prop.get('price', 'N/A')}€")
        print(f"     URL: {prop_url}")
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            print(f"     ❌ ERROR: This is a feed/search URL, should be rejected!")
    
    print(f"\n📈 Results: {valid_count} valid, {invalid_count} invalid")
    
    # Assert we extracted only individual listings
    assert len(properties) >= 2, "Should extract at least 2 properties"
    assert all(is_individual_listing_url(p.get('url', '')) for p in properties), \
        "All extracted URLs must be individual listings, not feed pages!"
    
    print("\n✅ Test PASSED: All extracted URLs are individual listings\n")


def test_individual_property_extraction():
    """Test extracting detailed info from individual property page."""
    print("=" * 80)
    print("TEST 3: Individual Property Detail Extraction")
    print("=" * 80)
    
    property_url = "https://casa.sapo.pt/imovel/apartamento-t1-faro-123456"
    
    # Verify URL is recognized as individual listing
    assert is_individual_listing_url(property_url), \
        "Property URL should be recognized as individual listing"
    print(f"\n✅ URL validated as individual listing: {property_url}")
    
    # Extract property data
    property_data = extract_property_from_casa_sapo_html(MOCK_INDIVIDUAL_PROPERTY_HTML, property_url)
    
    if property_data:
        print(f"\n📋 Extracted property details:")
        print(f"   Name: {property_data.get('name', 'N/A')}")
        print(f"   Type: {property_data.get('property_type', 'N/A')}")
        print(f"   Price: {property_data.get('price', 'N/A')}€")
        print(f"   Location: {property_data.get('location', 'N/A')}")
        print(f"   Bedrooms: {property_data.get('bedrooms', 'N/A')}")
        print(f"   Description: {property_data.get('description', 'N/A')[:100]}...")
        
        print("\n✅ Test PASSED: Successfully extracted property details\n")
    else:
        print("\n❌ Test FAILED: Could not extract property details\n")
        assert False, "Should extract property details from individual listing"


def test_complete_flow():
    """Test the complete flow: Feed → Individual URLs → Property Details."""
    print("=" * 80)
    print("TEST 4: Complete Scraping Flow")
    print("=" * 80)
    
    print("\n🔄 STEP 1: Scrape feed page to get individual listing URLs")
    base_url = "https://casa.sapo.pt/search?location=faro"
    properties_from_feed = extract_properties_from_casa_sapo_listing(MOCK_CASA_SAPO_FEED_HTML, base_url)
    
    print(f"   → Found {len(properties_from_feed)} properties in feed")
    
    print("\n🔄 STEP 2: Validate all URLs are individual listings (not feed pages)")
    individual_urls = []
    for prop in properties_from_feed:
        url = prop.get('url', '')
        if is_individual_listing_url(url):
            individual_urls.append(url)
            print(f"   ✅ Valid individual URL: {url}")
        else:
            print(f"   ❌ Rejected feed URL: {url}")
    
    print(f"\n   → {len(individual_urls)} individual listing URLs ready for detailed scraping")
    
    print("\n🔄 STEP 3: Simulate scraping individual property details")
    # In real implementation, we would scrape each individual URL
    # Here we simulate with mock data
    for i, url in enumerate(individual_urls[:2], 1):  # Limit to 2 for demo
        print(f"\n   Scraping property {i}: {url}")
        # Simulate extraction
        property_data = extract_property_from_casa_sapo_html(MOCK_INDIVIDUAL_PROPERTY_HTML, url)
        if property_data:
            print(f"   ✅ Extracted: {property_data.get('property_type', 'N/A')} - {property_data.get('price', 'N/A')}€")
        else:
            print(f"   ⚠️  Could not extract details (mock data)")
    
    print("\n✅ Test PASSED: Complete flow validated\n")
    
    # Assertions
    assert len(properties_from_feed) >= 2, "Should extract multiple properties from feed"
    assert len(individual_urls) >= 2, "Should have multiple valid individual URLs"
    assert len(individual_urls) == len(properties_from_feed), \
        "All feed properties should have valid individual URLs"


def main():
    """Run all scraping flow tests."""
    print("\n")
    print("🧪 " * 40)
    print("COMPLETE SCRAPING FLOW TESTS")
    print("Testing: Feed → Individual Listing URLs → Property Details")
    print("🧪 " * 40)
    print("\n")
    
    try:
        test_feed_extraction_casa_sapo()
        test_feed_extraction_idealista()
        test_individual_property_extraction()
        test_complete_flow()
        
        print("=" * 80)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 80)
        print("\n✅ The scraping flow correctly:")
        print("   1. Extracts individual listing URLs from feed pages")
        print("   2. Rejects feed/search page URLs")
        print("   3. Extracts detailed property info from individual listings")
        print("\n")
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print("💥 UNEXPECTED ERROR")
        print("=" * 80)
        print(f"Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
