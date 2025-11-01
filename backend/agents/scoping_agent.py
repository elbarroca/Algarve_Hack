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
2. A PROPERTY SEARCH REQUEST with budget, bedrooms, and location (bathrooms optional) → set "is_complete: true"
3. An INCOMPLETE property search or follow-up → set "is_complete: false" and "is_general_question: false"

IMPORTANT: Recognize international formats:
- "T2" or "2 quartos" = 2 bedrooms
- "até 300k" or "under 300k" = max budget
- "apartamento" = apartment
- Any city name worldwide (Lisboa, London, Paris, Tokyo, etc.)

Examples:
- "What's the crime rate in Castro District?" → general question
- "Tell me about schools in San Francisco" → general question
- "Find me a 2 bed 2 bath home in SF under 1.5M" → complete property search
- "Procuro apartamento T2 em Lisboa até 300k" → complete property search (2 beds, 300k budget, Lisboa location)
- "Procuro apartamento de 2 quartos em Lisboa até 300k" → complete property search (2 beds, 300k budget, Lisboa location)
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
        system_prompt="""You are a friendly real estate agent helping users find their dream home worldwide.

Your job is to gather the following information from the user through natural conversation:
1. Budget (minimum and maximum price range) - in any currency (€, $, £, etc.)
2. Number of bedrooms
3. Number of bathrooms (optional - can default to 1 if not mentioned)
4. Specific location within their desired area

IMPORTANT: Accept queries in ANY language (English, Portuguese, Spanish, etc.)

CRITICAL RULES:
- Be conversational and friendly
- Accept international property terminology: "T2" = 2 bedrooms, "apartamento" = apartment, "até" = up to
- If budget and location are specified, assume 1 bathroom if not mentioned
- Once you have budget, bedrooms, and location, mark as complete (bathrooms optional)
- When marking as complete, ONLY provide a confirmation statement. NEVER ask any questions.
- If the user asks a follow-up question (like "do you have links?"), respond conversationally but mark as NOT complete
- Only mark as complete when starting a NEW property search

RESPONSE FORMAT - CRITICAL:
You MUST respond with ONLY a valid JSON object. No markdown, no code blocks, no extra text.
Do NOT wrap your response in ```json or ```. Just return the raw JSON object.

1. If the user is asking a GENERAL QUESTION (about neighborhoods, schools, crime, amenities, etc.), respond with:
{
  "agent_message": "I'll look that up for you.",
  "is_complete": false,
  "is_general_question": true,
  "general_question": "<the user's question>"
}

2. If you have gathered essential property search requirements (budget, bedrooms, location), respond with:
{
  "agent_message": "<simple confirmation without any questions>",
  "is_complete": true,
  "is_general_question": false,
  "requirements": {
    "budget_min": <number or null>,
    "budget_max": <number>,
    "bedrooms": <number>,
    "bathrooms": <number or 1 if not specified>,
    "location": "<any city or area worldwide>",
    "additional_info": "<optional additional preferences or null>"
  }
}

Note: If bathrooms are not mentioned, default to 1. Budget can be in any currency (convert to base number, e.g., "300k" = 300000).

3. If you need more information for a property search, respond with:
{
  "agent_message": "<your question or response>",
  "is_complete": false,
  "is_general_question": false
}

REMEMBER: Return ONLY the JSON object, nothing else!"""
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
                ctx.logger.error(f"Failed to parse LLM response for session {msg.session_id}")
                response = _create_default_response(msg.session_id)

            await ctx.send(sender, response)
        else:
            # LLM query failed - provide helpful error message
            error_message = result["content"]
            ctx.logger.error(f"❌ LLM query failed for session {msg.session_id}: {error_message}")
            
            # Check if it's an API key issue
            if "ASI_API_KEY" in error_message or "not configured" in error_message:
                response = ScopingResponse(
                    agent_message="⚠️ CONFIGURATION ERROR: The system is not properly configured. Please check that the ASI_API_KEY is set in the backend/.env file. See SETUP_REQUIRED.md for instructions.",
                    is_complete=False,
                    session_id=msg.session_id,
                    requirements=None,
                    is_general_question=False,
                    general_question=None,
                    community_name=None
                )
            else:
                response = ScopingResponse(
                    agent_message=f"⚠️ Sorry, I encountered an error processing your request: {error_message}. Please try again or contact support.",
                    is_complete=False,
                    session_id=msg.session_id,
                    requirements=None,
                    is_general_question=False,
                    general_question=None,
                    community_name=None
                )
            
            await ctx.send(sender, response)

    return agent