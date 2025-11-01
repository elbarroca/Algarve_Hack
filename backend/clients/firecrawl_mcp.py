"""
Firecrawl MCP client for web scraping
"""
import os
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from typing import Optional, Dict, List


class FirecrawlMCPClient:
    """Client for Firecrawl MCP server"""
    
    def __init__(self):
        self.session = None
        self._stack = AsyncExitStack()
        self._connected = False
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
    
    async def connect(self):
        """Connect to Firecrawl MCP server"""
        if self._connected or not self.api_key:
            return
        
        # Use remote hosted Firecrawl MCP server
        url = f"https://mcp.firecrawl.dev/{self.api_key}/v2/mcp"
        
        try:
            read_stream, write_stream, _ = await self._stack.enter_async_context(
                streamablehttp_client(url)
            )
            self.session = await self._stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await self.session.initialize()
            self._connected = True
        except Exception as e:
            print(f"[Firecrawl MCP] Connection failed: {e}")
            self._connected = False
    
    async def disconnect(self):
        """Disconnect from Firecrawl MCP server"""
        if self._connected:
            await self._stack.aclose()
            self._connected = False
            self.session = None
    
    async def scrape(self, url: str, formats: Optional[List[str]] = None) -> Optional[Dict]:
        """Scrape a URL using Firecrawl MCP"""
        if not self.api_key:
            return None
        
        await self.connect()
        if not self._connected:
            return None
        
        try:
            formats = formats or ["html", "markdown"]
            result = await self.session.call_tool(
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
        except Exception as e:
            print(f"[Firecrawl MCP Scrape Error] {e}")
            return None
    
    async def batch_scrape(self, urls: List[str], formats: Optional[List[str]] = None) -> Optional[str]:
        """Start a batch scrape job"""
        if not self.api_key:
            return None
        
        await self.connect()
        if not self._connected:
            return None
        
        try:
            formats = formats or ["html", "markdown"]
            result = await self.session.call_tool(
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
                # Extract batch ID from response
                import re
                match = re.search(r'batch_[\w-]+', content_text)
                if match:
                    return match.group(0)
            return None
        except Exception as e:
            print(f"[Firecrawl MCP Batch Scrape Error] {e}")
            return None
    
    async def check_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Check status of a batch scrape job"""
        if not self.api_key:
            return None
        
        await self.connect()
        if not self._connected:
            return None
        
        try:
            result = await self.session.call_tool(
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

