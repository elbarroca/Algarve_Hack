"""
Firecrawl scraper for enhanced property scraping
"""
import os
import asyncio
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor
from firecrawl import Firecrawl

class FirecrawlScraper:
    """Wrapper for Firecrawl API to scrape property listings"""
    
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")
        
        # Import here to avoid error if not installed
        try:
            self.client = Firecrawl(api_key=api_key)
            self.executor = ThreadPoolExecutor(max_workers=3)
        except ImportError:
            raise ImportError("firecrawl-py package not installed. Run: pip install firecrawl-py")
    
    async def scrape_property_page(self, url: str) -> Optional[Dict]:
        """
        Scrape a single property detail page.
        Returns HTML content and structured data.
        """
        try:
            # Run synchronous Firecrawl call in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: self.client.scrape(
                    url,
                    formats=["html", "markdown"],
                    only_main_content=False,
                )
            )
            
            if result and result.get("success"):
                return {
                    "html": result.get("data", {}).get("html", ""),
                    "markdown": result.get("data", {}).get("markdown", ""),
                    "metadata": result.get("data", {}).get("metadata", {}),
                }
            return None
        except Exception as e:
            print(f"[Firecrawl Scrape Error] {e}")
            return None
    
    async def scrape_property_with_json(self, url: str, schema: Optional[Dict] = None) -> Optional[Dict]:
        """
        Scrape property page and extract structured JSON data.
        If schema is provided, uses it for extraction.
        """
        try:
            formats = ["html"]
            
            # Add JSON extraction if schema provided
            if schema:
                formats.append({
                    "type": "json",
                    "schema": schema,
                })
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                lambda: self.client.scrape(
                    url,
                    formats=formats,
                    only_main_content=False,
                )
            )
            
            if result and result.get("success"):
                data = result.get("data", {})
                return {
                    "html": data.get("html", ""),
                    "markdown": data.get("markdown", ""),
                    "json": data.get("json"),
                    "metadata": data.get("metadata", {}),
                }
            return None
        except Exception as e:
            print(f"[Firecrawl JSON Scrape Error] {e}")
            return None
    
    async def batch_scrape_properties(self, urls: List[str]) -> List[Dict]:
        """
        Batch scrape multiple property URLs.
        Returns list of scrape results.
        """
        try:
            loop = asyncio.get_event_loop()
            job = await loop.run_in_executor(
                self.executor,
                lambda: self.client.batch_scrape(
                    urls,
                    formats=["html", "markdown"],
                    poll_interval=2,
                    wait_timeout=300,  # 5 minutes timeout
                )
            )
            
            if job and job.get("status") == "completed":
                results = []
                for item in job.get("data", []):
                    results.append({
                        "html": item.get("html", ""),
                        "markdown": item.get("markdown", ""),
                        "metadata": item.get("metadata", {}),
                        "url": item.get("metadata", {}).get("sourceURL", ""),
                    })
                return results
            return []
        except Exception as e:
            print(f"[Firecrawl Batch Scrape Error] {e}")
            return []


def get_firecrawl_scraper() -> Optional[FirecrawlScraper]:
    """Get Firecrawl scraper instance if API key is available."""
    try:
        return FirecrawlScraper()
    except (ValueError, ImportError) as e:
        # Firecrawl API key not set or package not installed
        print(f"[Firecrawl] Not available: {e}")
        return None

