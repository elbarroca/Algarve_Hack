"""
Test URL validation for identifying individual property listings vs feed pages.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.scraper import is_individual_listing_url


def test_individual_listing_urls():
    """Test that individual listing URLs are correctly identified."""
    
    # Valid individual listing URLs (should return True)
    valid_urls = [
        # Casa Sapo
        "https://casa.sapo.pt/imovel/apartamento-t1-faro-123456",
        "https://casa.sapo.pt/imovel/moradia-algarve-789012",
        
        # Idealista
        "https://www.idealista.pt/imovel/123456.html",
        "https://www.idealista.pt/apartamento-123456-faro.html",
        "https://www.idealista.pt/moradia-789012-algarve.html",
        
        # ImOvirtual
        "https://www.imovirtual.com/anuncio/123456",
        "https://www.imovirtual.com/anuncio/apartamento-t2-faro-123456",
        
        # Generic patterns
        "https://example.com/property/123456",
        "https://example.com/detail/789012",
        "https://example.com/apartamento/123456",
        "https://example.com/casa-123456.html",
    ]
    
    print("✅ Testing VALID individual listing URLs:")
    for url in valid_urls:
        result = is_individual_listing_url(url)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {url}")
        if not result:
            print(f"    ERROR: Should be identified as individual listing!")
    
    print()


def test_feed_page_urls():
    """Test that feed/search page URLs are correctly rejected."""
    
    # Invalid feed/search URLs (should return False)
    invalid_urls = [
        # Search pages
        "https://casa.sapo.pt/search?q=faro",
        "https://www.idealista.pt/alugar-casas/faro",
        "https://www.idealista.pt/comprar-apartamentos/algarve",
        "https://www.imovirtual.com/results?location=faro",
        "https://example.com/listings?city=faro&bedrooms=2",
        
        # Category/browse pages
        "https://casa.sapo.pt/list/faro",
        "https://www.idealista.pt/venda-imoveis/algarve",
        "https://www.idealista.pt/aluguer-apartamentos/faro",
        
        # Search results
        "https://example.com/pesquisa/faro",
        "https://example.com/results",
        
        # Empty URLs
        "",
        None,
    ]
    
    print("❌ Testing INVALID feed/search page URLs:")
    for url in invalid_urls:
        result = is_individual_listing_url(url)
        status = "✅ PASS" if not result else "❌ FAIL"
        print(f"  {status}: {url}")
        if result:
            print(f"    ERROR: Should be rejected as feed/search page!")
    
    print()


def main():
    """Run all URL validation tests."""
    print("=" * 80)
    print("URL VALIDATION TESTS")
    print("=" * 80)
    print()
    
    test_individual_listing_urls()
    test_feed_page_urls()
    
    print("=" * 80)
    print("Tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
