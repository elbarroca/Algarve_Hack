"""
Scoping Agent - Collects user requirements for property search
"""
from uagents import Agent, Context
from models import ScopingRequest, ScopingResponse, UserRequirements
from llm_client import SimpleLLMAgent


def _build_conversation_context(conversation_history: list) -> str:
    """Build conversation context string from conversation history."""
    assert isinstance(conversation_history, list), "Conversation history must be a list"
    
    return "\n".join([
        f"{'User' if m['role'] == 'user' else 'Agent'}: {m['content']}"
        for m in conversation_history
    ])


def _build_requirements_prompt(conversation_text: str) -> str:
    """Build analysis prompt for LLM to determine user intent."""
    assert isinstance(conversation_text, str), "Conversation text must be a string"
    
    return f"""Based on the following conversation, determine the user's intent:

Conversation:
{conversation_text}

Determine if this is:
1. A GENERAL QUESTION (asking about neighborhoods, schools, crime, amenities, local info, etc.) → set "is_general_question: true"
2. A PROPERTY SEARCH REQUEST with all requirements (budget, bedrooms, bathrooms, location) → set "is_complete: true"
3. An INCOMPLETE property search or follow-up → set "is_complete: false" and "is_general_question: false"

Examples:
- "What's the crime rate in Castro District?" → general question
- "Tell me about schools in San Francisco" → general question
- "Find me a 2 bed 2 bath home in SF under 1.5M" → complete property search
- "I'm looking for a home" → incomplete (need more info)

Respond with a JSON object as specified in your instructions."""


def _validate_requirements(requirements_data: dict) -> UserRequirements:
    """Validate and create UserRequirements object from parsed LLM response."""
    assert isinstance(requirements_data, dict), "Requirements data must be a dictionary"
    
    # Validate required fields
    required_fields = ['budget_max', 'bedrooms', 'bathrooms', 'location']
    for field in required_fields:
        if field not in requirements_data:
            raise ValueError(f"Missing required field: {field}")
    
    return UserRequirements(**requirements_data)


def _create_default_response(session_id: str) -> ScopingResponse:
    """Create default response for error scenarios."""
    assert isinstance(session_id, str), "Session ID must be a string"
    
    return ScopingResponse(
        agent_message="How can I help you find a home?",
        is_complete=False,
        session_id=session_id,
        requirements=None
    )


def create_scoping_agent(port: int = 8001):
    """Create and configure the scoping agent for requirement gathering."""
    agent = Agent(
        name="scoping_agent",
        port=port,
        seed="scoping_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"]
    )

    # LLM client for conversation
    llm_client = SimpleLLMAgent(
        "scoping_agent",
        system_prompt="""You are a friendly real estate agent helping users find their dream home.

Your job is to gather the following information from the user through natural conversation:
1. Budget (minimum and maximum price range)
2. Number of bedrooms
3. Number of bathrooms
4. Specific location within their desired area

CRITICAL RULES:
- Be conversational and friendly
- Ask follow-up questions ONLY if you still need information
- Once you have ALL required information (budget, bedrooms, bathrooms, and location), mark as complete
- When marking as complete, ONLY provide a confirmation statement. NEVER ask any questions.
- If the user asks a follow-up question (like "do you have links?"), respond conversationally but mark as NOT complete
- Only mark as complete when starting a NEW property search

RESPONSE FORMATS:

1. If the user is asking a GENERAL QUESTION (about neighborhoods, schools, crime, amenities, etc.), respond with:
{
  "agent_message": "I'll look that up for you.",
  "is_complete": false,
  "is_general_question": true,
  "general_question": "<the user's question>"
}

2. If you have gathered ALL property search requirements (budget, bedrooms, bathrooms, location), respond with:
{
  "agent_message": "<simple confirmation without any questions>",
  "is_complete": true,
  "is_general_question": false,
  "requirements": {
    "budget_min": <number or null>,
    "budget_max": <number>,
    "bedrooms": <number>,
    "bathrooms": <number>,
    "location": "<city/area in Bay Area>",
    "additional_info": "<optional additional preferences or null>"
  }
}

3. If you need more information for a property search, respond with:
{
  "agent_message": "<your question or response>",
  "is_complete": false,
  "is_general_question": false
}"""
    )

    # Store conversation history per session
    conversations = {}

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Scoping Agent started at {ctx.agent.address}")

    @agent.on_message(model=ScopingRequest)
    async def handle_request(ctx: Context, sender: str, msg: ScopingRequest):
        """Handle scoping requests with intelligent conversation management."""
        # Initialize conversation history
        if msg.session_id not in conversations:
            conversations[msg.session_id] = []

        # Add user message to history
        conversations[msg.session_id].append({
            "role": "user",
            "content": msg.user_message
        })

        # Build conversation context
        conversation_text = _build_conversation_context(conversations[msg.session_id])
        prompt = _build_requirements_prompt(conversation_text)

        # Query LLM
        result = await llm_client.query_llm(prompt, temperature=0.1, max_tokens=300)

        if result["success"]:
            parsed = llm_client.parse_json_response(result["content"])

            if parsed:
                # DEBUG: Log the full parsed response
                ctx.logger.info(f"DEBUG - Parsed LLM response: {parsed}")
                ctx.logger.info(f"DEBUG - is_general_question: {parsed.get('is_general_question', False)}")
                ctx.logger.info(f"DEBUG - is_complete: {parsed.get('is_complete', False)}")

                # Store agent response in history
                conversations[msg.session_id].append({
                    "role": "assistant",
                    "content": parsed.get("agent_message", "")
                })

                # Build response
                requirements = None
                community_name = None
                if parsed.get("is_complete", False) and "requirements" in parsed:
                    requirements = UserRequirements(**parsed["requirements"])
                    # Extract community name from location
                    community_name = requirements.location if requirements else None
                    ctx.logger.info(f"Requirements gathered for session {msg.session_id}, community: {community_name}")

                response = ScopingResponse(
                    agent_message=parsed.get("agent_message", "How can I help you find a home?"),
                    is_complete=parsed.get("is_complete", False),
                    session_id=msg.session_id,
                    requirements=requirements,
                    is_general_question=parsed.get("is_general_question", False),
                    general_question=parsed.get("general_question", None),
                    community_name=community_name
                )
            else:
                response = _create_default_response(msg.session_id)

            await ctx.send(sender, response)
        else:
            response = _create_default_response(msg.session_id)
            await ctx.send(sender, response)

    return agent