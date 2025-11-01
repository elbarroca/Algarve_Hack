"""
General Agent - Handles general questions about areas, neighborhoods, etc.
"""
from uagents import Agent, Context
from models import GeneralRequest, GeneralResponse
from llm_client import SimpleLLMAgent
from clients.tavily import TavilyClient


def _build_search_query(question: str, context: str = None) -> str:
    """Build optimized search query from question and optional context."""
    assert isinstance(question, str), "Question must be a string"
    assert context is None or isinstance(context, str), "Context must be a string or None"
    
    search_query = question
    if context:
        # Extract location from context and append to search
        location = context.split(": ")[-1] if ": " in context else ""
        if location:
            search_query = f"{question} {location}"
    
    return search_query


def _build_llm_context(question: str, context: str = None, search_results: dict = None) -> str:
    """Build comprehensive context for LLM from question, context, and search results."""
    assert isinstance(question, str), "Question must be a string"
    assert context is None or isinstance(context, str), "Context must be a string or None"
    assert search_results is None or isinstance(search_results, dict), "Search results must be a dict or None"
    
    llm_context = f"User Question: {question}\n\n"
    
    if context:
        llm_context += f"Context: {context}\n\n"
    
    llm_context += "Search Results:\n\n"
    
    if search_results and search_results.get("results"):
        for idx, result in enumerate(search_results["results"][:5], 1):
            llm_context += f"Result {idx}:\n"
            llm_context += f"Title: {result.get('title', 'N/A')}\n"
            llm_context += f"URL: {result.get('url', 'N/A')}\n"
            llm_context += f"Content: {result.get('content', 'N/A')[:800]}...\n\n"
    
    return llm_context


def _validate_search_results(search_results: dict) -> bool:
    """Validate search results structure and content."""
    assert isinstance(search_results, dict), "Search results must be a dictionary"
    return search_results.get("success", False) and search_results.get("results")


async def _perform_search(tavily_client: TavilyClient, query: str) -> dict:
    """Perform advanced search using Tavily client."""
    assert hasattr(tavily_client, 'search'), "Tavily client must have search method"
    assert isinstance(query, str), "Query must be a string"
    
    return await tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=10
    )


async def _generate_response(llm_client: SimpleLLMAgent, prompt: str, session_id: str) -> GeneralResponse:
    """Generate response using LLM with error handling."""
    assert hasattr(llm_client, 'query_llm'), "LLM client must have query_llm method"
    assert hasattr(llm_client, 'parse_json_response'), "LLM client must have parse_json_response method"
    assert isinstance(prompt, str), "Prompt must be a string"
    assert isinstance(session_id, str), "Session ID must be a string"
    
    result = await llm_client.query_llm(prompt, temperature=0.3, max_tokens=800)
    
    if result["success"]:
        parsed = llm_client.parse_json_response(result["content"])
        
        if parsed and "answer" in parsed:
            return GeneralResponse(
                answer=parsed["answer"],
                session_id=session_id
            )
    
    # Fallback response
    return GeneralResponse(
        answer="I apologize, but I'm having trouble formulating an answer right now. Could you try rephrasing your question?",
        session_id=session_id
    )


def create_general_agent(port: int = 8003):
    """Create and configure the general agent for location-based questions."""
    agent = Agent(
        name="general_agent",
        port=port,
        seed="general_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"]
    )

    # LLM client for answering questions
    llm_client = SimpleLLMAgent(
        "general_agent",
        system_prompt="""You are a knowledgeable Algarve Portuguese real estate assistant who answers general questions about neighborhoods, areas, schools, amenities, and local information.

Your job is to provide helpful, accurate information based on search results.

CRITICAL RULES:
- Answer questions conversationally and naturally
- Use the search results to provide accurate information
- If search results don't contain the answer, say so honestly
- Focus on information relevant to someone looking for a home
- Be concise but informative

Respond with a JSON object in this format:
{
  "answer": "<your detailed answer to the user's question>"
}"""
    )

    # Tavily client
    tavily = TavilyClient()

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"General Agent started at {ctx.agent.address}")

    @agent.on_message(model=GeneralRequest)
    async def handle_request(ctx: Context, sender: str, msg: GeneralRequest):
        """Handle general questions with comprehensive search and LLM analysis."""
        # Build search query
        search_query = _build_search_query(msg.question, msg.context)
        
        # Perform search
        search_results = await _perform_search(tavily, search_query)
        
        # Handle search failure
        if not _validate_search_results(search_results):
            response = GeneralResponse(
                answer=f"I'm having trouble searching for that information right now. Please try again.",
                session_id=msg.session_id
            )
            await ctx.send(sender, response)
            return
        
        # Build context for LLM
        llm_context = _build_llm_context(msg.question, msg.context, search_results)
        prompt = f"""{llm_context}

Based on the search results above, answer the user's question: "{msg.question}"

Provide a clear, helpful answer. If the search results don't contain enough information to answer the question, say so honestly.

Respond with a JSON object as specified in your instructions."""
        
        # Generate and send response
        response = await _generate_response(llm_client, prompt, msg.session_id)
        await ctx.send(sender, response)

    return agent