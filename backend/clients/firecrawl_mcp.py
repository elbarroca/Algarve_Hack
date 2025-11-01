"""
Firecrawl MCP client for web scraping
Fixed async context management to prevent cross-task errors
"""
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from typing import Optional, Dict, List
import asyncio


class FirecrawlMCPClient:
    """Client for Firecrawl MCP server with proper async context management"""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self._semaphore = asyncio.Semaphore(10)  # Allow up to 10 concurrent requests for faster processing
    
    async def scrape(self, url: str, formats: Optional[List[str]] = None) -> Optional[Dict]:
        """Scrape a URL using Firecrawl MCP with proper async context management"""
        if not self.api_key:
            return None
        
        # Use a semaphore to limit concurrent connections (max 5 at a time)
        async with self._semaphore:
            try:
                url_mcp = f"https://mcp.firecrawl.dev/{self.api_key}/v2/mcp"
                
                # Create and use session in the same async context
                async with streamablehttp_client(url_mcp) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        
                        formats = formats or ["html", "markdown"]
                        result = await session.call_tool(
                            "firecrawl_scrape",
                            {
                                "url": url,
                                "formats": formats,
                                "onlyMainContent": False,
                            }
                        )
                        
                        if result and result.content:
                            content_text = result.content[0].text
                            import json
                            try:
                                # Parse JSON response
                                data = json.loads(content_text)
                                return {
                                    "html": data.get("html", ""),
                                    "markdown": data.get("markdown", ""),
                                    "metadata": data.get("metadata", {}),
                                }
                            except:
                                # Return raw text if not JSON
                                return {
                                    "html": content_text,
                                    "markdown": content_text,
                                    "metadata": {},
                                }
                        return None
            except RuntimeError as e:
                # Suppress async context errors - they're non-critical
                if "cancel scope" in str(e):
                    print(f"[Firecrawl MCP] Async context warning (non-critical): {e}")
                    return None
                raise
            except Exception as e:
                print(f"[Firecrawl MCP Scrape Error] {e}")
                return None
    
    async def batch_scrape(self, urls: List[str], formats: Optional[List[str]] = None) -> Optional[str]:
        """Start a batch scrape job"""
        if not self.api_key:
            return None
        
        async with self._lock:
            try:
                url_mcp = f"https://mcp.firecrawl.dev/{self.api_key}/v2/mcp"
                async with streamablehttp_client(url_mcp) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        
                        formats = formats or ["html", "markdown"]
                        result = await session.call_tool(
                            "firecrawl_batch_scrape",
                            {
                                "urls": urls,
                                "options": {
                                    "formats": formats,
                                    "onlyMainContent": False,
                                }
                            }
                        )
                        
                        if result and result.content:
                            content_text = result.content[0].text
                            import re
                            match = re.search(r'batch_[\w-]+', content_text)
                            if match:
                                return match.group(0)
                        return None
            except RuntimeError as e:
                if "cancel scope" in str(e):
                    print(f"[Firecrawl MCP] Async context warning (non-critical): {e}")
                    return None
                raise
            except Exception as e:
                print(f"[Firecrawl MCP Batch Scrape Error] {e}")
                return None
    
    async def check_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Check status of a batch scrape job"""
        if not self.api_key:
            return None
        
        async with self._lock:
            try:
                url_mcp = f"https://mcp.firecrawl.dev/{self.api_key}/v2/mcp"
                async with streamablehttp_client(url_mcp) as (read_stream, write_stream, _):
                    async with ClientSession(read_stream, write_stream) as session:
                        await session.initialize()
                        
                        result = await session.call_tool(
                            "firecrawl_check_batch_status",
                            {"id": batch_id}
                        )
                        
                        if result and result.content:
                            import json
                            content_text = result.content[0].text
                            try:
                                return json.loads(content_text)
                            except:
                                return {"status": "unknown", "data": content_text}
                        return None
            except RuntimeError as e:
                if "cancel scope" in str(e):
                    print(f"[Firecrawl MCP] Async context warning (non-critical): {e}")
                    return None
                raise
            except Exception as e:
                print(f"[Firecrawl MCP Check Batch Error] {e}")
                return None


def get_firecrawl_mcp_client() -> Optional[FirecrawlMCPClient]:
    """Get Firecrawl MCP client instance if API key is available"""
    try:
        client = FirecrawlMCPClient()
        if client.api_key:
            return client
        return None
    except Exception as e:
        print(f"[Firecrawl MCP] Not available: {e}")
        return None

