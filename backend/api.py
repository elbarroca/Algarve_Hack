"""
Negotiation Workflow - FastAPI server for handling property negotiations
=========================================================================

This workflow handles:
1. Probing a property for negotiation intelligence
2. (Future) Calling Vapi agent with intelligence + user preferences
3. (Future) Sending email confirmation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import uvicorn
from uagents import Bureau

from agents.prober_agent import create_prober_agent
from models import ProberRequest, ProberResponse, ProberFinding
from llm_client import SimpleLLMAgent


# Pydantic Models for REST API
class NegotiateRequest(BaseModel):
    """Request from frontend to start negotiation"""
    address: str
    name: str
    email: str
    additional_info: Optional[str] = None


class NegotiateResponse(BaseModel):
    """Simplified response with just summary and success status"""
    success: bool
    message: str
    leverage_score: float
    next_actions: List[str]


# Initialize FastAPI and Agents
app = FastAPI(title="Estate Negotiation Workflow")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create prober agent
prober_agent = create_prober_agent(port=8007)
prober_address = prober_agent.address

# Create LLM summarizer
llm_summarizer = SimpleLLMAgent(
    name="NegotiationSummarizer",
    system_prompt="You are an expert real estate negotiation analyst. Summarize negotiation conversations concisely."
)

# Session storage for responses
prober_responses = {}


@prober_agent.on_message(model=ProberResponse)
async def handle_prober_response(ctx, sender: str, msg: ProberResponse):
    """Store prober response for the REST endpoint to pick up"""
    ctx.logger.info(f"Received prober response for session {msg.session_id}")
    prober_responses[msg.session_id] = msg


# REST API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "negotiation_workflow"}


@app.post("/api/negotiate", response_model=NegotiateResponse)
async def negotiate_property(request: NegotiateRequest):
    """
    Start negotiation process for a property.
    For now, this only handles probing.

    Future: Will call Vapi agent and send email confirmation.
    """
    print(f"\n{'='*60}")
    print(f"🔍 Starting negotiation for: {request.address}")
    print(f"   User: {request.name} ({request.email})")
    print(f"{'='*60}\n")

    # Generate session ID
    import uuid
    session_id = str(uuid.uuid4())

    # Send probe request to prober agent
    probe_request = ProberRequest(
        address=request.address,
        session_id=session_id
    )

    print(f"📤 Sending probe request to prober agent...")
    await prober_agent._ctx.send(prober_address, probe_request)

    # Wait for prober response (with timeout)
    max_wait = 60  # 60 seconds timeout
    waited = 0
    while session_id not in prober_responses and waited < max_wait:
        await asyncio.sleep(0.5)
        waited += 0.5

    if session_id not in prober_responses:
        print(f"❌ Timeout waiting for prober response")
        raise HTTPException(
            status_code=504,
            detail="Timeout waiting for property intelligence. Please try again."
        )

    # Get prober response
    prober_result = prober_responses.pop(session_id)

    print(f"\n✅ Prober completed!")
    print(f"   Found {len(prober_result.findings)} findings")
    print(f"   Leverage Score: {prober_result.leverage_score}/10")
    print(f"   Assessment: {prober_result.overall_assessment[:100]}...")

    # Generate AI summary and next actions based on findings
    print(f"\n📝 Generating negotiation summary with LLM...")
    summary_prompt = f"""Based on the following property intelligence, create a concise negotiation summary and actionable next steps.

Property: {request.address}
User: {request.name}
Additional Context: {request.additional_info or 'None provided'}

Intelligence Findings ({len(prober_result.findings)} items):
{chr(10).join([f"- {f.category}: {f.summary} (leverage: {f.leverage_score}/10)" for f in prober_result.findings[:5]])}

Overall Assessment: {prober_result.overall_assessment}
Leverage Score: {prober_result.leverage_score}/10

Generate ONLY valid JSON with this exact structure:
{{
  "summary": "A 2-3 sentence summary of the negotiation position and key findings",
  "next_actions": [
    "Specific action item 1",
    "Specific action item 2",
    "Specific action item 3"
  ]
}}

Focus on practical, actionable steps the buyer should take next."""

    summary_result = await llm_summarizer.query_with_json(summary_prompt, temperature=0.5)

    if summary_result.get("success"):
        summary_data = summary_result.get("data", {})
        ai_summary = summary_data.get("summary", prober_result.overall_assessment)
        next_actions = summary_data.get("next_actions", [])
    else:
        ai_summary = prober_result.overall_assessment
        next_actions = [
            "Review the identified leverage points carefully",
            "Prepare your negotiation strategy based on findings",
            "Contact the listing agent to initiate discussions"
        ]

    print(f"✅ Summary generated with {len(next_actions)} action items")

    # TODO: Call Vapi agent with prober_result + user preferences

    return NegotiateResponse(
        success=True,
        message=ai_summary,
        leverage_score=prober_result.leverage_score,
        next_actions=next_actions
    )


def start_workflow():
    """Start the negotiation workflow with agents and FastAPI server"""
    print("\n" + "="*60)
    print("🤝 Estate Negotiation Workflow Starting")
    print("="*60)
    print(f"Prober Agent: {prober_address}")
    print("="*60 + "\n")

    # Run FastAPI with uvicorn in the same process
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
    server = uvicorn.Server(config)

    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run prober agent in background
    async def run_agent():
        await prober_agent._startup()
        # Keep agent running
        while True:
            await asyncio.sleep(1)

    # Run both agent and server
    async def run_all():
        agent_task = asyncio.create_task(run_agent())
        await server.serve()

    try:
        loop.run_until_complete(run_all())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down negotiation workflow...")
    finally:
        loop.close()


if __name__ == "__main__":
    start_workflow()