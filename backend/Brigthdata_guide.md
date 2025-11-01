# Bright Data MCP Integration

## Overview

The research agent now uses **Bright Data MCP** instead of Tavily for property searches. This provides more reliable and structured real estate listing data by scraping Zillow directly.

## How It Works

### 1. **Architecture**

```
User Query
    ↓
Coordinator → Scoping Agent → Research Agent
                                    ↓
                            BrightDataClient (MCP)
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            search_engine tool              scrape_as_markdown tool
            (Google Search)                 (Scrapes Idealist page)
                    ↓                               ↓
            Find Idealista URLs        →       Extract property listings
```

### 2. **MCP Integration**

The `BrightDataClient` class (backend/agents/brightdata_client.py) connects to Bright Data's MCP server:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to Bright Data MCP
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@brightdata/mcp"],
    env={**os.environ}
)

read, write = await stdio_client(server_params)
session = ClientSession(read, write)
await session.__aenter__()
```

### 3. **Search Flow**

1. **Build search query**: "zillow homes for sale in San Francisco 2 bedrooms 2 bathrooms $1.5M"

2. **Call `search_engine` tool** via MCP:
   ```python
   result = await session.call_tool(
       "search_engine",
       arguments={
           "query": search_query,
           "engine": "google"
       }
   )
   ```

3. **Extract Zillow URL** from search results

4. **Call `scrape_as_markdown` tool** to get listing page content:
   ```python
   scrape_result = await session.call_tool(
       "scrape_as_markdown",
       arguments={"url": category_url}
   )
   ```

5. **Parse markdown** to extract structured property data:
   - Address
   - City
   - Price
   - Bedrooms
   - Bathrooms
   - Square footage
   - URL

6. **Filter by user requirements** (budget, bedrooms, bathrooms)

7. **Return PropertyListing objects** to coordinator

## Benefits Over Tavily

1. **More Reliable Data**: Direct scraping from Zillow ensures accurate property information
2. **Structured Extraction**: Parses Zillow's markdown format for consistent data
3. **No LLM Parsing**: Properties are extracted deterministically, not via LLM inference
4. **Better Filtering**: Can precisely filter by price, bedrooms, bathrooms before returning results

## Setup

### Requirements

1. Add to `backend/requirements.txt`:
   ```
   mcp>=1.0.0
   ```

2. Bright Data MCP server is installed automatically via `npx -y @brightdata/mcp`

3. No API key needed for basic usage

### Running

The MCP client automatically connects when the research agent receives a request:

```bash
cd backend
python main.py
```

## Files Modified

- `backend/agents/brightdata_client.py` - New MCP client
- `backend/agents/research_agent.py` - Updated to use Bright Data instead of Tavily
- `backend/requirements.txt` - Added MCP SDK dependency

## Testing

Test the integration:

```bash
# From frontend
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me a 2 bedroom 2 bathroom home in San Francisco under 1.5M",
    "session_id": "test123"
  }'
```

The response will include real Zillow listings scraped via Bright Data MCP.