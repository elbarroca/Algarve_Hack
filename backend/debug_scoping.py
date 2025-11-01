"""
Debug script to test scoping agent LLM parsing
"""
import asyncio
from llm_client import SimpleLLMAgent

async def test_scoping_llm():
    llm_client = SimpleLLMAgent(
        "scoping_agent_debug",
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

RESPONSE FORMATS:

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
}"""
    )
    
    test_queries = [
        "Procuro apartamento de 2 quartos em Lisboa até 300k",
        "Find me a 2 bedroom apartment in Lisbon under 300000 euros",
        "I need a 3 bed house in San Francisco under 1.5 million"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Testing query: {query}")
        print(f"{'='*80}")
        
        conversation_text = f"User: {query}"
        
        prompt = f"""Based on the following conversation, determine the user's intent:

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
        
        result = await llm_client.query_llm(prompt, temperature=0.1, max_tokens=300)
        
        if result["success"]:
            print(f"\n✅ LLM Response:")
            print(result["content"])
            
            parsed = llm_client.parse_json_response(result["content"])
            if parsed:
                print(f"\n✅ Parsed JSON:")
                import json
                print(json.dumps(parsed, indent=2))
            else:
                print(f"\n❌ Failed to parse JSON")
        else:
            print(f"\n❌ LLM Query Failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_scoping_llm())

