"""
Community Analysis Agent - Analyzes community news, safety, schools, and housing metrics
"""
import os
import json
from openai import OpenAI
from uagents import Agent, Context
from tavily import TavilyClient
from dotenv import load_dotenv
from models import CommunityAnalysisRequest, CommunityAnalysisResponse

load_dotenv()


def _fetch_articles_by_category(location: str, category: str, max_results: int = 15) -> list:
    """Fetch articles by category using Tavily search with standardized logic."""
    assert isinstance(location, str), "Location must be a string"
    assert isinstance(category, str), "Category must be a string"
    assert isinstance(max_results, int), "Max results must be an integer"
    
    category_queries = {
        'news': f"{location} local news community safety crime development",
        'schools': f"{location} schools ratings rankings education quality greatschools niche",
        'housing': f"{location} housing prices per square foot average home size zillow redfin realtor"
    }
    
    search_query = category_queries.get(category, f"{location} {category}")
    
    try:
        client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
        response = client.search(
            query=search_query,
            max_results=max_results,
            search_depth="advanced",
            include_domains=[],
            exclude_domains=[]
        )

        articles = []
        if response and 'results' in response:
            for result in response['results']:
                articles.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })
        return articles
    except Exception:
        return []


def _format_articles_for_llm(articles: list, category: str) -> str:
    """Format articles for LLM consumption with category-specific logic."""
    assert isinstance(articles, list), "Articles must be a list"
    assert isinstance(category, str), "Category must be a string"
    
    if not articles:
        return f"No {category}-related articles found.\n\n"
    
    formatted = f"Here are {category} articles about this location:\n\n"
    for i, article in enumerate(articles, 1):
        formatted += f"{i}. {article['title']}\n"
        formatted += f"   Content: {article['content'][:300]}...\n"
        formatted += f"   URL: {article['url']}\n\n"
    
    return formatted


async def _query_community_model(location: str) -> str:
    """Query ASI model for community analysis using standardized data processing."""
    assert isinstance(location, str), "Location must be a string"
    
    # Fetch all required data categories
    articles = _fetch_articles_by_category(location, 'news', 20)
    school_articles = _fetch_articles_by_category(location, 'schools', 15)
    housing_articles = _fetch_articles_by_category(location, 'housing', 15)

    # Format for LLM
    articles_text = _format_articles_for_llm(articles, 'community news')
    school_text = _format_articles_for_llm(school_articles, 'education')
    housing_text = _format_articles_for_llm(housing_articles, 'housing')

    client = OpenAI(
        base_url='https://api.asi1.ai/v1',
        api_key=os.getenv('ASI_API_KEY'),
    )

    system_prompt = """
You are a community news analyst. You will be given real news articles about a location, and you need to analyze them.
You MUST respond with ONLY valid JSON in the following format (no additional text):

{
  "location": "location name",
  "overall": {
    "score": 7.9,
    "explanation": "Brief explanation of overall rating"
  },
  "safety": {
    "score": 7.5,
    "positive_stories": [
      {"title": "story title 1", "summary": "brief summary", "url": "article url"},
      {"title": "story title 2", "summary": "brief summary", "url": "article url"}
    ],
    "negative_stories": [
      {"title": "story title 1", "summary": "brief summary", "url": "article url"},
      {"title": "story title 2", "summary": "brief summary", "url": "article url"}
    ]
  },
  "schools": {
    "score": 8.2,
    "explanation": "Brief explanation of school rating based on the education articles"
  },
  "housing_avg": {
    "housing_price_per_square_foot": 739,
    "average_house_size_square_foot": 1921
  }
}

FOLLOW THESE INSTRUCTIONS STRICTLY:
- All scores (overall, safety, schools) must be numbers from 0-10 with precision to tenths (e.g., 7.3, 8.5).
- The overall score should be calculated as the average of safety and schools scores.
- Analyze the provided news articles and categorize them into positive and negative stories under the safety section.
- The included url links to the real news articles.
- Choose the 2 most relevant positive stories and 2 most relevant negative stories for safety.
- Base your safety score on the content of the articles, crime reports, community development news, and quality of life indicators.
- Base your schools score on school quality indicators, ratings from sources like GreatSchools or Niche, test scores, and education-related news.
- Extract housing_price_per_square_foot and average_house_size_square_foot from the housing articles (as integer values).
- If housing data cannot be found in the articles, provide reasonable estimates based on your knowledge of the area.

YOU WILL CHOOSE THE NEWS ARTICLES THAT YOU INCLUDE ACCORDING TO THE FOLLOWING CRITERIA (LISTED IN ORDER OF IMPORTANCE):
- Choose sources that are specific news articles about the location, not generic news websites.
- Choose sources that are relevant and informative to the location.
- Choose sources that are most recent.
"""

    try:
        response = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze community news and safety for: {location}\n\n{articles_text}\n{school_text}\n{housing_text}"},
            ],
            max_tokens=2048,
        )
        return str(response.choices[0].message.content)
    except Exception:
        raise


def _clean_json_response(response_text: str) -> dict:
    """Clean and parse JSON response from LLM with robust error handling."""
    assert isinstance(response_text, str), "Response text must be a string"
    
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]

    return json.loads(cleaned_text.strip())


def _build_response_data(response_data: dict, location: str, session_id: str) -> CommunityAnalysisResponse:
    """Build standardized response object from parsed JSON data."""
    assert isinstance(response_data, dict), "Response data must be a dictionary"
    assert isinstance(location, str), "Location must be a string"
    assert isinstance(session_id, str), "Session ID must be a string"
    
    overall_data = response_data.get("overall", {})
    safety_data = response_data.get("safety", {})
    schools_data = response_data.get("schools", {})
    housing_data = response_data.get("housing_avg", {})

    return CommunityAnalysisResponse(
        location=response_data.get("location", location),
        overall_score=float(overall_data.get("score", 0.0)),
        overall_explanation=overall_data.get("explanation", "N/A"),
        safety_score=float(safety_data.get("score", 0.0)),
        positive_stories=safety_data.get("positive_stories", []),
        negative_stories=safety_data.get("negative_stories", []),
        school_rating=float(schools_data.get("score", 0.0)),
        school_explanation=schools_data.get("explanation", "N/A"),
        housing_price_per_square_foot=int(housing_data.get("housing_price_per_square_foot", 0)),
        average_house_size_square_foot=int(housing_data.get("average_house_size_square_foot", 0)),
        session_id=session_id
    )


def _create_error_response(location: str, session_id: str, error_type: str) -> CommunityAnalysisResponse:
    """Create standardized error response for various failure scenarios."""
    assert isinstance(location, str), "Location must be a string"
    assert isinstance(session_id, str), "Session ID must be a string"
    assert isinstance(error_type, str), "Error type must be a string"
    
    return CommunityAnalysisResponse(
        location=location,
        overall_score=0.0,
        overall_explanation=f"Error: {error_type}",
        safety_score=0.0,
        positive_stories=[],
        negative_stories=[],
        school_rating=0.0,
        school_explanation=f"Error: {error_type}",
        housing_price_per_square_foot=0,
        average_house_size_square_foot=0,
        session_id=session_id
    )


def create_community_analysis_agent(port: int = 8006):
    """Create and configure the community analysis agent for comprehensive location intelligence."""
    agent = Agent(
        name="community_analysis_agent",
        port=port,
        seed="community_analysis_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"]
    )

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Community Analysis Agent started at {ctx.agent.address}")

    @agent.on_message(model=CommunityAnalysisRequest)
    async def handle_request(ctx: Context, sender: str, msg: CommunityAnalysisRequest):
        """Handle community analysis requests with comprehensive data gathering and LLM analysis."""
        try:
            # Query the model with the location name
            response_text = await _query_community_model(msg.location_name)
            
            # Parse and process the JSON response
            response_data = _clean_json_response(response_text)
            response = _build_response_data(response_data, msg.location_name, msg.session_id)
            
            await ctx.send(sender, response)

        except json.JSONDecodeError:
            response = _create_error_response(msg.location_name, msg.session_id, "parsing JSON response")
            await ctx.send(sender, response)

        except Exception:
            response = _create_error_response(msg.location_name, msg.session_id, "querying model")
            await ctx.send(sender, response)

    return agent