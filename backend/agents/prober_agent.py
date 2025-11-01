"""
Prober Agent - Gathers intelligence about properties for negotiation leverage
============================================================================

This agent combines Tavily (for finding relevant sources) and BrightData (for scraping)
to gather information that can be used in negotiations. The LLM handles analysis.

Categories of intelligence:
- Time on market (longer = more desperate seller)
- Price history (reductions indicate flexibility)
- Property issues (repairs, violations, permits)
- Owner situation (foreclosure, estate sale, divorce, etc.)
- Market conditions (buyer's vs seller's market)
"""

from uagents import Agent, Context
from models import ProberRequest, ProberResponse, ProberFinding
from clients.tavily import TavilyClient
from clients.brigthdata import BrightDataClient
from llm_client import SimpleLLMAgent
import asyncio


class ProberLLMAgent(SimpleLLMAgent):
    """LLM agent specialized for analyzing property intelligence and extracting negotiation leverage"""

    def __init__(self):
        system_prompt = """You are a real estate negotiation analyst. Extract actionable intelligence from property data.
Return ONLY valid JSON, no markdown formatting or additional text."""
        super().__init__(name="ProberLLM", system_prompt=system_prompt)

    async def analyze_property_intel(self, address: str, scraped_content: list) -> dict:
        """
        Analyze scraped property content and extract negotiation leverage.
        Returns structured findings.
        """
        # Format scraped content for LLM
        content_summary = ""
        for idx, item in enumerate(scraped_content, 1):
            url = item.get("url", "Unknown")
            text = item.get("content", "")[:2000]  # Limit to first 2000 chars per source
            content_summary += f"\n\n--- Source {idx}: {url} ---\n{text}\n"

        prompt = f"""You are a ruthless real estate negotiation analyst. Your job is to find NEGATIVE information, red flags, and weaknesses about this property that a buyer can use as leverage to negotiate a LOWER price.

Property Address: {address}

Scraped Information:
{content_summary}

FOCUS ON NEGATIVE INFORMATION ONLY. Extract leverage points in these categories:

1. **time_on_market**:
   - How many days on market? (longer = desperate seller)
   - Price reductions? (indicates overpriced or lack of interest)
   - Multiple listing attempts?

2. **price_history**:
   - Recent price drops
   - Bought high, selling low (financial pressure)
   - Overpriced compared to comps

3. **property_issues**:
   - Foundation, roof, plumbing problems
   - Code violations, unpermitted work
   - Deferred maintenance
   - Needed repairs mentioned in listing

4. **owner_situation**:
   - Foreclosure risk, tax liens
   - Estate sale (heirs want quick cash)
   - Divorce (forced sale)
   - Job relocation (time pressure)
   - Financial distress signals

5. **market_conditions**:
   - Buyer's market indicators
   - High inventory in area
   - Declining neighborhood values
   - Economic factors favoring buyers

**IMPORTANT**: Only include findings that give the BUYER an advantage. Skip positive information. Be specific with numbers (days on market, price reductions, etc).

For each finding, provide:
- category (one of the above)
- summary (1-2 sentences highlighting the NEGATIVE aspect)
- leverage_score (0-10, how useful for negotiation - higher = more leverage)
- details (specific numbers, dates, problems)
- source_url (if applicable)

Also provide:
- overall_assessment: A 2-3 sentence summary of the buyer's negotiation position focusing on WEAKNESSES found
- leverage_score: Overall score 0-10 (10 = strong buyer leverage due to many issues found)

Return ONLY valid JSON in this exact format:
{{
  "findings": [
    {{
      "category": "time_on_market",
      "summary": "...",
      "leverage_score": 7.5,
      "details": "...",
      "source_url": "..."
    }}
  ],
  "overall_assessment": "...",
  "leverage_score": 6.5
}}

If you cannot find any information, return an empty findings array and low leverage_score.
"""

        result = await self.query_with_json(prompt, temperature=0.1)

        if result["success"]:
            return result["data"]
        else:
            return {
                "findings": [],
                "overall_assessment": f"Analysis failed: {result.get('error', 'Unknown error')}",
                "leverage_score": 0.0
            }


def create_prober_agent(port: int = 8006):
    agent = Agent(
        name="prober_agent",
        port=port,
        seed="prober_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    tavily = TavilyClient()
    brightdata = BrightDataClient()
    llm_agent = ProberLLMAgent()

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Prober Agent started at {ctx.agent.address}")

    @agent.on_message(model=ProberRequest)
    async def handle_probe_request(ctx: Context, sender: str, msg: ProberRequest):
        ctx.logger.info(f"Probing property: {msg.address}")

        # No longer accepting test addresses - warn but continue
        is_test_address = any(word in msg.address.lower() for word in ["test", "123 test", "sample", "example", "fake"])
        if is_test_address:
            ctx.logger.error(f"❌ Test address detected: {msg.address}")
            ctx.logger.error(f"   Prober agent requires REAL property addresses")
            ctx.logger.error(f"   Use skip_research=True in negotiate request to bypass prober")
            # Return empty results for test addresses
            await ctx.send(sender, ProberResponse(
                address=msg.address,
                findings=[],
                overall_assessment="Test address provided. No research performed. Use skip_research=True to call directly.",
                leverage_score=0.0,
                session_id=msg.session_id
            ))
            return

        # Step 1: Use Tavily to find relevant sources about this property
        # Use more specific search query focusing on property listings and real estate
        search_query = f'"{msg.address}" property listing realtor agent contact OR "{msg.address}" real estate for sale rent'
        ctx.logger.info(f"Tavily search: {search_query}")
        tavily_result = await tavily.search(
            query=search_query,
            search_depth="advanced",
            max_results=3,
            include_domains=["zillow.com", "realtor.com", "redfin.com", "trulia.com", "rightmove.com", "idealista.pt"]
        )

        all_urls = []
        if tavily_result.get("success"):
            results = tavily_result.get("results", [])
            for result in results:
                url = result.get("url")
                # Skip Zillow and Redfin as they're already covered by research agent
                if url and "zillow.com" not in url.lower() and "redfin.com" not in url.lower():
                    all_urls.append({
                        "url": url,
                        "title": result.get("title", ""),
                        "content": result.get("content", "")
                    })
        else:
            ctx.logger.warning(f"Tavily search failed: {tavily_result.get('error')}")

        ctx.logger.info(f"Found {len(all_urls)} unique URLs from Tavily")

        # Step 2: Use BrightData to scrape the top URLs (limit to 2-3 max)
        scraped_content = []
        urls_to_scrape = all_urls[:3]  # Max 3 sources

        for item in urls_to_scrape:
            url = item["url"]
            ctx.logger.info(f"Scraping with BrightData: {url}")

            try:
                scrape_result = await brightdata.call(
                    "scrape_as_markdown",
                    {"url": url}
                )

                if scrape_result.get("success"):
                    markdown_content = scrape_result.get("output", "")
                    scraped_content.append({
                        "url": url,
                        "title": item["title"],
                        "content": markdown_content,
                        "tavily_snippet": item["content"]  # Keep Tavily's snippet too
                    })
                    ctx.logger.info(f"Successfully scraped {url}")
                else:
                    ctx.logger.warning(f"BrightData scrape failed for {url}: {scrape_result.get('error')}")
                    # Fall back to Tavily content
                    scraped_content.append({
                        "url": url,
                        "title": item["title"],
                        "content": item["content"],
                        "tavily_snippet": item["content"]
                    })
            except Exception as e:
                ctx.logger.warning(f"Error scraping {url}: {e}")
                # Fall back to Tavily content
                scraped_content.append({
                    "url": url,
                    "title": item["title"],
                    "content": item["content"],
                    "tavily_snippet": item["content"]
                })

        ctx.logger.info(f"Scraped {len(scraped_content)} sources")

        # Step 3: Use LLM to analyze and extract negotiation leverage
        ctx.logger.info("Analyzing content with LLM...")
        try:
            # Add timeout to LLM analysis (60 seconds)
            analysis = await asyncio.wait_for(
                llm_agent.analyze_property_intel(msg.address, scraped_content),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            ctx.logger.error("❌ LLM analysis timed out - no fallback data will be provided")
            # No fallback - return empty results
            analysis = {
                "findings": [],
                "overall_assessment": f"LLM analysis timed out for {msg.address}. No property intelligence available.",
                "leverage_score": 0.0
            }

        # Convert findings to ProberFinding models
        findings = []
        for finding_dict in analysis.get("findings", []):
            try:
                findings.append(ProberFinding(
                    category=finding_dict.get("category", "unknown"),
                    summary=finding_dict.get("summary", ""),
                    leverage_score=float(finding_dict.get("leverage_score", 0.0)),
                    details=finding_dict.get("details", ""),
                    source_url=finding_dict.get("source_url")
                ))
            except Exception as e:
                ctx.logger.warning(f"Failed to create ProberFinding: {e}")
                continue

        # If no findings were extracted, log warning but don't generate fake data
        if len(findings) == 0:
            ctx.logger.warning(f"⚠️ No findings extracted from analysis")
            ctx.logger.warning(f"   No relevant property information found online for {msg.address}")
            ctx.logger.warning(f"   Consider using skip_research=True to bypass prober agent")
            # Keep empty findings list - no fake data

        ctx.logger.info(f"Extracted {len(findings)} findings with overall leverage score: {analysis.get('leverage_score', 0.0)}")
        ctx.logger.info(f"Step 3: LLM analysis complete")
        ctx.logger.info(f"Step 4: Sending response back to coordinator...")

        # Send response
        await ctx.send(sender, ProberResponse(
            address=msg.address,
            findings=findings,
            overall_assessment=analysis.get("overall_assessment", "No assessment available"),
            leverage_score=float(analysis.get("leverage_score", 0.0)),
            session_id=msg.session_id
        ))
        
        ctx.logger.info(f"✅ Step 4: Response sent successfully to {sender[:20]}...")

    return agent