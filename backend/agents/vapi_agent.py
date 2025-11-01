"""
Vapi Agent - Handles AI phone call negotiations with listing agents
====================================================================

This agent:
1. Takes property intelligence from prober agent
2. Builds a system prompt with all the leverage data
3. Updates the Vapi assistant with the prompt
4. Initiates a phone call to the listing agent
"""

from uagents import Agent, Context
from models import Model
from typing import Optional, Dict, Any, List
from clients.vapi import VapiClient
import os
import json


# Vapi Models for uAgents
class VapiRequest(Model):
    """Request to make a negotiation call via Vapi"""
    property_address: str
    user_name: str
    user_email: str
    user_preferences: str
    intelligence: Dict[str, Any]  # The full intelligence JSON from prober
    session_id: str


class VapiResponse(Model):
    """Response from Vapi agent"""
    call_id: Optional[str] = None
    status: str
    message: str
    session_id: str
    call_summary: Optional[str] = None


def _format_findings_text(findings: list) -> str:
    """Format findings for the system prompt with leverage scores."""
    assert isinstance(findings, list), "Findings must be a list"
    
    findings_text = ""
    for idx, finding in enumerate(findings, 1):
        findings_text += f"""
{idx}. {finding['category'].upper().replace('_', ' ')} (Leverage Score: {finding['leverage_score']}/10)
   - Summary: {finding['summary']}
   - Details: {finding['details']}
"""
        if finding.get('source_url'):
            findings_text += f"   - Source: {finding['source_url']}\n"

    return findings_text


def _calculate_price_reduction(leverage_score: int) -> tuple[str, str]:
    """Calculate suggested price reduction based on leverage score."""
    assert isinstance(leverage_score, int), "Leverage score must be an integer"
    assert 0 <= leverage_score <= 10, "Leverage score must be between 0 and 10"
    
    if leverage_score >= 7:
        return "5-10%", "high leverage position"
    elif leverage_score >= 5:
        return "3-5%", "moderate leverage position"
    else:
        return "1-3%", "limited leverage position"


def _build_negotiation_strategy(vapi_context: Dict[str, Any]) -> Dict[str, str]:
    """Build comprehensive negotiation strategy based on intelligence data."""
    assert isinstance(vapi_context, dict), "Context must be a dictionary"
    
    leverage_score = vapi_context['intelligence']['leverage_score']
    findings = vapi_context['intelligence']['findings']
    
    # Calculate strategy based on leverage score
    reduction_range, leverage_desc = _calculate_price_reduction(leverage_score)
    
    strategy = {
        'reduction_range': reduction_range,
        'leverage_desc': leverage_desc,
        'key_talking_points': '\n'.join([f"- {f['summary']}" for f in findings[:3]])
    }
    
    return strategy


def build_system_prompt(vapi_context: Dict[str, Any]) -> str:
    """Build the system prompt for Vapi assistant with intelligence data."""
    assert isinstance(vapi_context, dict), "Context must be a dictionary"
    assert 'property' in vapi_context, "Context must contain property data"
    assert 'user' in vapi_context, "Context must contain user data"
    assert 'intelligence' in vapi_context, "Context must contain intelligence data"
    
    property_addr = vapi_context['property']['address']
    user_name = vapi_context['user']['name']
    user_prefs = vapi_context['user']['preferences']
    leverage_score = vapi_context['intelligence']['leverage_score']
    assessment = vapi_context['intelligence']['overall_assessment']
    findings = vapi_context['intelligence']['findings']

    # Build strategy
    strategy = _build_negotiation_strategy(vapi_context)
    findings_text = _format_findings_text(findings)

    return f"""You are an AI negotiation agent representing the buyer {user_name} for the property at {property_addr}.

You are on a PHONE CALL with the listing agent to negotiate a better price. Your goal is to use the intelligence data below to get the LOWEST possible price for your client.

====================
BUYER INFORMATION
====================
Name: {user_name}
Preferences: {user_prefs}

====================
PROPERTY INTELLIGENCE
====================
Overall Leverage Score: {leverage_score}/10 (higher = more buyer leverage)

Overall Assessment:
{assessment}

Key Findings (USE THESE AS LEVERAGE):
{findings_text}

====================
NEGOTIATION STRATEGY
====================

1. OPENING:
   - Identify yourself as representing {user_name}
   - Express serious interest in the property
   - Mention you've done thorough market research

2. PRESENT CONCERNS (use the findings above):
   - Reference specific data points from findings
   - Focus on HIGH leverage score items first (8+ scores)
   - Be specific with numbers (days on market, price reductions, etc.)
   - Frame as "market analysis" not criticism

3. REQUEST PRICE REDUCTION:
   - Based on the leverage score and findings, suggest a price adjustment
   - You are in a {strategy['leverage_desc']} - request {strategy['reduction_range']} reduction
   - Justify with specific findings

4. HANDLE OBJECTIONS:
   - If they dispute findings, ask for their counter-data
   - Emphasize your client's serious interest and ability to close
   - Reference buyer's preferences: {user_prefs}
   - Stay professional but persistent

5. CLOSING:
   - Try to get verbal agreement on adjusted price
   - Offer to submit formal offer immediately
   - Get next steps (inspection, paperwork, etc.)

====================
RULES (MUST FOLLOW)
====================
- Keep responses BRIEF (under 75 words per turn)
- Be conversational and natural (you're on a phone call)
- Use ONLY the intelligence data provided - do NOT fabricate facts
- Stay professional and respectful
- Focus on DATA and MARKET CONDITIONS, not personal attacks
- Follow Fair Housing laws - no discriminatory language
- Do NOT use emojis or special formatting

====================
EXAMPLE OPENING
====================
"Hi, this is calling on behalf of {user_name} regarding the property at {property_addr}. We're very interested, but our market analysis has identified some concerns we'd like to discuss. Do you have a moment to talk about the pricing?"

====================
KEY TALKING POINTS
====================
Based on your intelligence, emphasize:
{strategy['key_talking_points']}

Remember: Your job is to get the LOWEST price possible while being professional. Use the intelligence data strategically!""".strip()


def _validate_vapi_context(context: Dict[str, Any]) -> None:
    """Validate Vapi context structure before processing."""
    assert isinstance(context, dict), "Context must be a dictionary"
    
    required_keys = ['property', 'user', 'intelligence']
    for key in required_keys:
        assert key in context, f"Missing required context key: {key}"
    
    # Validate nested structure
    assert 'address' in context['property'], "Property must have address"
    assert 'name' in context['user'], "User must have name"
    assert 'leverage_score' in context['intelligence'], "Intelligence must have leverage_score"
    assert 'overall_assessment' in context['intelligence'], "Intelligence must have overall_assessment"
    assert 'findings' in context['intelligence'], "Intelligence must have findings"


def create_vapi_agent(port: int = 8008):
    """Create and configure the Vapi agent for property negotiation calls."""
    agent = Agent(
        name="vapi_agent",
        port=port,
        seed="vapi_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    # Initialize Vapi client
    my_phone_number = os.getenv("VAPI_MY_PHONE_NUMBER", os.getenv("VAPI_TARGET_PHONE"))

    try:
        vapi_client = VapiClient()
    except Exception:
        vapi_client = None

    @agent.on_event("startup")
    async def startup(ctx: Context):
        ctx.logger.info(f"Vapi Agent started at {ctx.agent.address}")

    @agent.on_message(model=VapiRequest)
    async def handle_vapi_request(ctx: Context, sender: str, msg: VapiRequest):
        ctx.logger.info(f"📞 Vapi call request for: {msg.property_address}")
        ctx.logger.info(f"   User: {msg.user_name}")
        ctx.logger.info(f"   Leverage Score: {msg.intelligence.get('leverage_score', 0)}/10")
        ctx.logger.info(f"   Findings: {len(msg.intelligence.get('findings', []))} leverage points")
        ctx.logger.info(f"   📋 Using property intelligence data from prober agent")

        if not vapi_client:
            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message="Vapi API key not configured",
                session_id=msg.session_id
            ))
            return

        try:
            # Validate and build context
            vapi_context = {
                "property": {"address": msg.property_address},
                "user": {
                    "name": msg.user_name,
                    "email": msg.user_email,
                    "preferences": msg.user_preferences
                },
                "intelligence": msg.intelligence
            }
            
            _validate_vapi_context(vapi_context)
            
            # Build system prompt and first message using found house data
            # The intelligence dict contains all property findings from the prober agent
            system_prompt = build_system_prompt(vapi_context)
            
            # Create first message that references the property intelligence
            property_address = msg.property_address
            leverage_score = msg.intelligence.get('leverage_score', 0)
            findings_count = len(msg.intelligence.get('findings', []))
            
            first_message = (
                f"Hi, I'm calling on behalf of {msg.user_name} regarding the property at {property_address}. "
                f"We've conducted thorough market research and found {findings_count} key leverage points "
                f"with an overall leverage score of {leverage_score} out of 10. "
                f"Do you have a moment to discuss the pricing?"
            )

            # Update Vapi assistant with property intelligence
            ctx.logger.info(f"Updating assistant with property intelligence:")
            ctx.logger.info(f"   - Property: {property_address}")
            ctx.logger.info(f"   - Leverage Score: {leverage_score}/10")
            ctx.logger.info(f"   - Findings: {findings_count} leverage points")
            
            success = vapi_client.update_assistant(
                system_prompt=system_prompt,
                first_message=first_message
            )

            if not success:
                raise Exception("Failed to update Vapi assistant")

            # HACKATHON: Always call YOUR phone number (not listing agent)
            # This allows you to receive the call and test the negotiation
            ctx.logger.info(f"📞 Calling YOUR number: {my_phone_number}")
            ctx.logger.info(f"   (This is for hackathon demo - you'll receive the call)")
            
            call_id = vapi_client.create_call(customer_phone=my_phone_number)

            if not call_id:
                raise Exception("Failed to create call")

            # Wait for call completion and get analysis
            call_summary = vapi_client.wait_for_call_analysis(call_id, timeout_seconds=120)

            # Send success response
            await ctx.send(sender, VapiResponse(
                call_id=call_id,
                status="success",
                message="Negotiation call completed",
                session_id=msg.session_id,
                call_summary=call_summary or "Call completed. Analysis not yet available."
            ))

        except Exception as e:
            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message=f"Failed to initiate call: {str(e)}",
                session_id=msg.session_id
            ))

    return agent