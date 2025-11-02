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
from agents.vapi_prompts import build_student_housing_prompt, build_first_message
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
    # Structured outcomes from call
    availability_date: Optional[str] = None
    price_flexibility: Optional[str] = None
    tenant_requirements: Optional[str] = None
    next_steps: Optional[list] = None


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


def _calculate_price_reduction(leverage_score: float) -> tuple[str, str]:
    """Calculate suggested price reduction based on leverage score."""
    # Convert to int if it's a float
    leverage_score_int = int(round(leverage_score))
    assert 0 <= leverage_score_int <= 10, "Leverage score must be between 0 and 10"
    
    if leverage_score_int >= 7:
        return "5-10%", "high leverage position"
    elif leverage_score_int >= 5:
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
    """Build the optimized system prompt for Vapi assistant."""
    assert isinstance(vapi_context, dict), "Context must be a dictionary"
    assert 'property' in vapi_context, "Context must contain property data"
    assert 'user' in vapi_context, "Context must contain user data"
    assert 'intelligence' in vapi_context, "Context must contain intelligence data"

    property_data = vapi_context['intelligence'].get('property', vapi_context['property'])
    property_addr = property_data.get('address', vapi_context['property']['address'])
    user_name = vapi_context['user']['name']
    user_prefs = vapi_context['user']['preferences']
    leverage_score = vapi_context['intelligence']['leverage_score']
    findings = vapi_context['intelligence']['findings']

    # Extract location from address or use default
    location = property_addr.split(',')[-1].strip() if ',' in property_addr else property_addr

    # Extract property price and format it
    property_price = None
    price_value = property_data.get('price')
    if price_value:
        if isinstance(price_value, dict):
            amount = price_value.get('amount')
            is_rent = price_value.get('is_rent', False)
            if amount:
                property_price = f"€{amount:,}{'/month' if is_rent else ''}"
        elif isinstance(price_value, (int, float)):
            property_price = f"€{price_value:,}"

    # Extract property details
    property_details = {
        'bedrooms': property_data.get('bedrooms'),
        'bathrooms': property_data.get('bathrooms'),
        'area_m2': property_data.get('area_m2'),
    }

    # Use optimized prompt from vapi_prompts module
    return build_student_housing_prompt(
        student_name=user_name,
        location=location,
        property_address=property_addr,
        leverage_score=leverage_score,
        findings=findings,
        user_preferences=user_prefs,
        property_price=property_price,
        property_details=property_details
    )


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


async def parse_call_outcomes(call_summary: str, llm_client) -> dict:
    """
    Parse VAPI call summary to extract structured outcomes.

    Args:
        call_summary: The call summary/transcript from VAPI
        llm_client: LLM client for parsing

    Returns:
        Dictionary with structured outcomes:
        - availability_date: When property is available
        - price_flexibility: Any price negotiation mentioned
        - tenant_requirements: Landlord's tenant preferences
        - next_steps: What to do next
    """
    if not call_summary or call_summary == "":
        return {
            "availability_date": None,
            "price_flexibility": None,
            "tenant_requirements": None,
            "next_steps": []
        }

    prompt = f"""Analyze this property negotiation call summary and extract specific information:

Call Summary:
{call_summary}

Extract the following information and return as JSON:
1. **availability_date**: When is the property available? (extract date/timeframe if mentioned)
2. **price_flexibility**: Is there flexibility on price? What was discussed about pricing?
3. **tenant_requirements**: What qualities/requirements does the landlord want in a tenant?
4. **next_steps**: List of 2-3 specific next steps mentioned or implied

Return ONLY valid JSON in this format:
{{
  "availability_date": "string or null",
  "price_flexibility": "string or null",
  "tenant_requirements": "string or null",
  "next_steps": ["step 1", "step 2"]
}}

If information is not mentioned in the summary, use null for that field."""

    try:
        from llm_client import SimpleLLMAgent
        parser = SimpleLLMAgent(
            name="OutcomeParser",
            system_prompt="You are an expert at extracting structured information from conversation summaries."
        )
        result = await parser.query_with_json(prompt, temperature=0.1)

        if result.get("success"):
            return result.get("data", {})
        else:
            print(f"⚠️ Failed to parse outcomes: {result.get('error')}")
            return {
                "availability_date": None,
                "price_flexibility": None,
                "tenant_requirements": None,
                "next_steps": []
            }
    except Exception as e:
        print(f"❌ Error parsing call outcomes: {e}")
        return {
            "availability_date": None,
            "price_flexibility": None,
            "tenant_requirements": None,
            "next_steps": []
        }


def create_vapi_agent(port: int = 8008):
    """Create and configure the Vapi agent for property negotiation calls."""
    agent = Agent(
        name="vapi_agent",
        port=port,
        seed="vapi_agent_seed",
        endpoint=[f"http://localhost:{port}/submit"],
    )

    # Initialize Vapi client
    my_phone_number = os.getenv("VAPI_MY_PHONE_NUMBER", os.getenv("VAPI_TARGET_PHONE", "+15551234567"))

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
        ctx.logger.info(f"   🔍 Vapi client available: {vapi_client is not None}")

        if not vapi_client:
            ctx.logger.error("❌ Vapi client not initialized!")
            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message="Vapi API key not configured",
                session_id=msg.session_id
            ))
            return

        try:
            # Get property address early for use throughout the function
            property_address = msg.property_address
            
            # Validate and build context
            vapi_context = {
                "property": {"address": property_address},
                "user": {
                    "name": msg.user_name,
                    "email": msg.user_email,
                    "preferences": msg.user_preferences
                },
                "intelligence": msg.intelligence
            }
            
            _validate_vapi_context(vapi_context)
            
            # Build system prompt and first message using optimized prompts
            system_prompt = build_system_prompt(vapi_context)

            # Extract location and property price for first message
            location = property_address.split(',')[-1].strip() if ',' in property_address else property_address

            # Extract property price for first message
            property_data = msg.intelligence.get('property', {})
            property_price = None
            price_value = property_data.get('price')
            if price_value:
                if isinstance(price_value, dict):
                    amount = price_value.get('amount')
                    is_rent = price_value.get('is_rent', False)
                    if amount:
                        property_price = f"€{amount:,}{'/month' if is_rent else ''}"
                elif isinstance(price_value, (int, float)):
                    property_price = f"€{price_value:,}"

            # Use optimized first message
            first_message = build_first_message(
                student_name=msg.user_name,
                location=location,
                property_address=property_address,
                property_price=property_price
            )

            ctx.logger.info(f"   - Property price: {property_price or 'Not specified'}")

            # Update Vapi assistant with property intelligence
            leverage_score = msg.intelligence.get('leverage_score', 0)
            findings_count = len(msg.intelligence.get('findings', []))
            
            # Use VAPI default with most human-like male voice (Harry)
            # Note: Transcriber only supports English, but assistant can speak in Portuguese
            voice_id = "Harry"  # Most human-like male voice - clear, energetic, professional
            
            ctx.logger.info(f"Updating assistant with property intelligence:")
            ctx.logger.info(f"   - Property: {property_address}")
            ctx.logger.info(f"   - Location: {location}")
            ctx.logger.info(f"   - User: {msg.user_name}")
            ctx.logger.info(f"   - Leverage Score: {leverage_score}/10")
            ctx.logger.info(f"   - Findings: {findings_count} leverage points")
            ctx.logger.info(f"   - Voice: {voice_id} (VAPI default - most human-like male)")
            
            success = vapi_client.update_assistant(
                system_prompt=system_prompt,
                first_message=first_message,
                voice_id=voice_id
            )
            

            if not success:
                raise Exception("Failed to update Vapi assistant")

            # 🎯 LIVE DEMO MODE: Always call demo target phone
            # For live demos, we ALWAYS use the configured VAPI_TARGET_PHONE
            # This ensures the demo calls the correct number regardless of listing data

            if my_phone_number:
                ctx.logger.info(f"🎭 LIVE DEMO MODE: Using configured target phone")
                ctx.logger.info(f"📞 Calling demo phone: {my_phone_number}")
                ctx.logger.info(f"   Property: {property_address}")
                ctx.logger.info(f"   User: {msg.user_name}")
                target_phone = my_phone_number
            else:
                # Fallback to listing agent phone if demo phone not configured
                property_data = msg.intelligence.get("property", {})
                contact_phone = property_data.get("contact_phone") or property_data.get("seller_phone")

                ctx.logger.info(f"🔍 No demo phone configured, checking listing contact:")
                ctx.logger.info(f"   Contact phone found: {contact_phone}")

                if contact_phone:
                    ctx.logger.info(f"📞 Calling property listing agent: {contact_phone}")
                    target_phone = contact_phone
                else:
                    error_msg = "No demo phone configured and no listing contact phone found"
                    ctx.logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)
            
            ctx.logger.info(f"📞 Creating Vapi call to: {target_phone}")
            ctx.logger.info(f"   Final phone number: {target_phone}")
            ctx.logger.info(f"   Vapi client initialized: {vapi_client is not None}")
            
            # Validate phone number format (should be E.164: +1234567890)
            if not target_phone.startswith("+"):
                ctx.logger.warning(f"⚠️ Phone number doesn't start with '+', adding it: {target_phone}")
                # Try to add + if missing
                if target_phone.startswith("00"):
                    target_phone = "+" + target_phone[2:]
                elif target_phone.startswith("0"):
                    ctx.logger.warning(f"⚠️ Phone number starts with 0, may need country code")
                else:
                    target_phone = "+" + target_phone
            
            ctx.logger.info(f"🔨 INVOKING vapi_client.create_call() with phone: {target_phone}")
            call_id = vapi_client.create_call(customer_phone=target_phone)
            ctx.logger.info(f"📥 create_call() returned: {call_id}")

            if not call_id:
                # Check if this is a rate limit issue (daily call limit)
                error_msg = f"Failed to create Vapi call to {target_phone}"
                
                ctx.logger.error(error_msg)
                
                # Send error response instead of raising exception
                await ctx.send(sender, VapiResponse(
                    call_id=None,
                    status="error",
                    message="Could not initiate call. This may be due to daily call limits on VAPI-bought numbers. Consider importing your own Twilio number for unlimited calls.",
                    session_id=msg.session_id
                ))
                return

            ctx.logger.info(f"✅ Call created! Call ID: {call_id}")
            
            # Immediately verify call status
            import time
            time.sleep(3)  # Wait a moment for call to initialize
            call_status_data = vapi_client.get_call_status(call_id)
            if call_status_data:
                status = call_status_data.get("status", "unknown")
                ctx.logger.info(f"📞 Initial call status: {status}")
                
                if status in ["queued", "ringing", "in-progress"]:
                    ctx.logger.info(f"✅ Call is connecting! Status: {status}")
                elif status in ["ended", "failed"]:
                    error_info = call_status_data.get("error") or call_status_data.get("endReason", "Unknown")
                    ctx.logger.warning(f"⚠️ Call ended/failed immediately: {status} - {error_info}")
                    ctx.logger.warning(f"   This may indicate a connection issue")
                else:
                    ctx.logger.info(f"📊 Call status: {status}")
            else:
                ctx.logger.warning(f"⚠️ Could not retrieve initial call status")
            
            ctx.logger.info(f"⏳ Waiting for call completion and analysis (max 120s)...")

            # Wait for call completion and get analysis
            # Use shorter timeout to prevent hanging
            call_summary = vapi_client.wait_for_call_analysis(call_id, timeout_seconds=120)

            # Parse outcomes from call summary
            outcomes = {}
            if call_summary:
                ctx.logger.info(f"✅ Call completed! Summary: {call_summary[:100]}...")
                ctx.logger.info(f"🔍 Parsing call outcomes...")
                try:
                    outcomes = await parse_call_outcomes(call_summary, None)
                    ctx.logger.info(f"✅ Outcomes parsed: {outcomes}")
                except Exception as e:
                    ctx.logger.error(f"❌ Failed to parse outcomes: {e}")
                    outcomes = {}
            else:
                ctx.logger.info(f"⏳ Call still in progress or analysis not ready yet")
                ctx.logger.info(f"   Call ID: {call_id} - you can check status later")

            # Send success response (even if call is still in progress)
            await ctx.send(sender, VapiResponse(
                call_id=call_id,
                status="success",
                message="Negotiation call initiated successfully",
                session_id=msg.session_id,
                call_summary=call_summary or f"Call {call_id} initiated. Analysis pending.",
                availability_date=outcomes.get("availability_date"),
                price_flexibility=outcomes.get("price_flexibility"),
                tenant_requirements=outcomes.get("tenant_requirements"),
                next_steps=outcomes.get("next_steps", [])
            ))

        except Exception as e:
            error_details = str(e)
            ctx.logger.error(f"❌ Error in Vapi call: {error_details}")
            import traceback
            ctx.logger.error(traceback.format_exc())
            
            await ctx.send(sender, VapiResponse(
                call_id=None,
                status="error",
                message=f"Failed to initiate call: {error_details}",
                session_id=msg.session_id
            ))

    return agent