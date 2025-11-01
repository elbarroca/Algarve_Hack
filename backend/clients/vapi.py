"""
Vapi Client - Low-level wrapper for Vapi REST API
==================================================

This is a reusable utility class for interacting with Vapi.
The vapi_agent.py uses this client to make actual phone calls.
"""

import requests
import os
import json
from typing import Dict, Any, Optional


class VapiClient:
    """Client for interacting with Vapi REST API"""

    def __init__(self, api_key: Optional[str] = None):
        # Use PRIVATE key for backend API operations (create call, update assistant)
        # Public key is only for client-side Web SDK
        self.api_key = api_key or os.getenv("VAPI_PRIVATE_API_KEY") or os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"

        if not self.api_key:
            raise Exception("VAPI_PRIVATE_API_KEY or VAPI_API_KEY not found in environment variables")

        print(f"🔑 Using VAPI API key: {self.api_key[:20]}... (backend operations require private key)")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Default IDs (can be overridden via environment variables)
        self.assistant_id = os.getenv("VAPI_ASSISTANT_ID")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")

        if not self.assistant_id:
            raise Exception("VAPI_ASSISTANT_ID not found in environment variables")

        if not self.phone_number_id:
            raise Exception("VAPI_PHONE_NUMBER_ID not found in environment variables")

    @staticmethod
    def validate_phone_number(phone: str) -> tuple[bool, str]:
        """
        Validate and format phone number to E.164 format.

        Args:
            phone: Phone number string

        Returns:
            Tuple of (is_valid, formatted_phone or error_message)
        """
        if not phone:
            return False, "Phone number is empty"

        # Remove common formatting characters
        cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")

        # Check if it starts with +
        if not cleaned.startswith("+"):
            # Try to add + if it looks like an international number
            if cleaned.startswith("00"):
                cleaned = "+" + cleaned[2:]
            elif len(cleaned) >= 10:
                # Assume it's missing the + and country code
                return False, f"Phone number must start with + and country code. Got: {phone}"
            else:
                return False, f"Invalid phone number format: {phone}"

        # Basic validation: should be + followed by 10-15 digits
        if not cleaned[1:].isdigit():
            return False, f"Phone number must contain only digits after +. Got: {cleaned}"

        if len(cleaned) < 11 or len(cleaned) > 16:  # +1 + 10 digits minimum, +999 + 12 digits max
            return False, f"Phone number length invalid (should be 11-16 chars with +). Got: {cleaned} (length: {len(cleaned)})"

        # Log validation details
        print(f"   ✅ Phone number validation passed:")
        print(f"      Original: {phone}")
        print(f"      Cleaned: {cleaned}")
        print(f"      Length: {len(cleaned)} chars")
        print(f"      Country code: {cleaned[:2] if len(cleaned) > 2 else 'N/A'}")

        return True, cleaned

    def update_assistant(
        self,
        system_prompt: str,
        first_message: str,
        assistant_id: Optional[str] = None,
        language: str = "en",
        voice_id: str = "Harry"
    ) -> bool:
        """
        Update the Vapi assistant with new system prompt and first message.

        Args:
            system_prompt: The system prompt for the assistant
            first_message: The opening message for the call
            assistant_id: Optional assistant ID (uses default if not provided)
            language: Language code (kept for compatibility, but transcriber only supports "en")
            voice_id: VAPI voice ID to use (default: "Harry" - most human-like male voice)

        Returns:
            True if successful, False otherwise
        """
        aid = assistant_id or self.assistant_id
        url = f"{self.base_url}/assistant/{aid}"

        payload = {
            "firstMessage": first_message,
            "model": {
                "provider": "openai",
                "model": "gpt-4o-mini",  # Faster model for quicker responses
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    }
                ],
                "temperature": 0.8,  # Higher for more natural, varied responses (avoids repetition)
                "maxTokens": 200  # Allow slightly longer responses for natural flow
            },
            # Configure transcriber - assembly-ai only supports English
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-3",
                "language": "en"  # Only supports English
            },
            # Use VAPI default provider with most human-like male voice
            "voice": {
                "provider": "vapi",  # VAPI default provider
                "voiceId": voice_id  # VAPI voice: Harry (most human-like male), Elliot (friendly), etc.
            }
        }

        try:
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to update assistant: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return False

    def create_call(
        self,
        customer_phone: str,
        assistant_id: Optional[str] = None,
        phone_number_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a phone call via Vapi.
        Uses the /call endpoint (not /call/phone) according to Vapi API docs.

        Args:
            customer_phone: Phone number to call (e.g., "+18587331359")
            assistant_id: Optional assistant ID
            phone_number_id: Optional phone number ID

        Returns:
            Call ID if successful, None otherwise
        """
        # Validate and format phone number
        is_valid, result = self.validate_phone_number(customer_phone)
        if not is_valid:
            print(f"❌ Invalid phone number: {result}")
            return None

        validated_phone = result
        print(f"✅ Phone number validated: {customer_phone} → {validated_phone}")
        
        # Log phone number details for debugging
        print(f"📱 Phone number details:")
        print(f"   Original: {customer_phone}")
        print(f"   Validated: {validated_phone}")
        print(f"   Length: {len(validated_phone)} chars")
        print(f"   Country code: {validated_phone[:2]}")

        aid = assistant_id or self.assistant_id
        pnid = phone_number_id or self.phone_number_id

        # Use /call endpoint (not /call/phone) per Vapi API docs
        url = f"{self.base_url}/call"

        payload = {
            "assistantId": aid,
            "phoneNumberId": pnid,
            "customer": {
                "number": validated_phone
            }
        }

        print(f"📞 Creating Vapi call:")
        print(f"   URL: {url}")
        print(f"   Assistant ID: {aid}")
        print(f"   Phone Number ID: {pnid}")
        print(f"   Customer Phone: {validated_phone}")

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            print(f"\n📡 Vapi API Response:")
            print(f"   Status Code: {response.status_code}")
            
            # Check status code first
            if response.status_code not in [200, 201]:
                error_text = response.text
                print(f"❌ API returned non-success status: {response.status_code}")
                print(f"   Response text: {error_text}")
                
                # Check for specific error types
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "")
                    
                    # Detect daily call limit error
                    if "Daily Outbound Call Limit" in error_message or "daily outbound call limit" in error_message.lower():
                        print(f"\n⚠️  DAILY CALL LIMIT REACHED:")
                        print(f"   VAPI-bought numbers have daily limits.")
                        print(f"   Consider importing your own Twilio number for unlimited calls.")
                        print(f"   This is a rate limit, not a system error.")
                        
                except:
                    pass
                
                response.raise_for_status()
            
            # Parse response
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response text: {response.text}")
                data = {}
            
            call_id = data.get("id")
            
            if not call_id:
                print(f"⚠️ Warning: No call ID in response")
                print(f"   Trying alternative fields...")
                call_id = data.get("callId") or data.get("call_id")
            
            if call_id:
                print(f"✅ Call created successfully! Call ID: {call_id}")
                
                # Immediately check call status to verify it's actually connecting
                print(f"🔍 Verifying call status...")
                import time
                time.sleep(2)  # Wait a moment for call to initialize
                
                call_status_data = self.get_call_status(call_id)
                if call_status_data:
                    status = call_status_data.get("status", "unknown")
                    print(f"📞 Call status: {status}")
                    
                    # Check if call is in a good state
                    if status in ["queued", "ringing", "in-progress"]:
                        print(f"✅ Call is connecting! Status: {status}")
                    elif status == "ended":
                        print(f"⚠️ Call ended immediately - may have failed to connect")
                        # Get more details
                        error = call_status_data.get("error") or call_status_data.get("endReason")
                        if error:
                            print(f"   Error/Reason: {error}")
                    elif status == "failed":
                        print(f"❌ Call failed to connect")
                        error = call_status_data.get("error") or call_status_data.get("endReason")
                        if error:
                            print(f"   Error: {error}")
                    else:
                        print(f"⚠️ Unexpected call status: {status}")
                    
                    # Log phone number details for debugging
                    customer_data = call_status_data.get("customer", {})
                    if customer_data:
                        print(f"   Customer number: {customer_data.get('number', 'N/A')}")
                else:
                    print(f"⚠️ Could not retrieve call status immediately")
                
                return call_id
            else:
                print(f"❌ No call ID found in response")
                print(f"   Full response: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create call: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response status: {e.response.status_code}")
                print(f"   Response body: {e.response.text}")
                try:
                    error_data = e.response.json()
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
            return None

    def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a call by ID"""
        url = f"{self.base_url}/call/{call_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get call status: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def wait_for_call_analysis(self, call_id: str, timeout_seconds: int = 120, poll_interval: float = 2.0) -> Optional[str]:
        """
        Wait for a call to complete and return its analysis summary.
        Vapi automatically generates analysis after call ends.
        Returns immediately if call is still in progress after timeout.

        Args:
            call_id: The ID of the call
            timeout_seconds: Maximum time to wait for analysis (default 120s)
            poll_interval: How often to poll for status (default 2s)

        Returns:
            The call summary from analysis, or None if timeout/error
        """
        import time

        start_time = time.time()

        print(f"Waiting for call {call_id} to complete and generate analysis...")

        while (time.time() - start_time) < timeout_seconds:
            call_data = self.get_call_status(call_id)

            if not call_data:
                print(f"Failed to get call status, will retry...")
                time.sleep(poll_interval)
                continue

            status = call_data.get("status", "")
            print(f"Call status: {status}")

            # Check if call has ended
            if status == "ended":
                # Call has ended, check if analysis is available
                analysis = call_data.get("analysis", {})
                summary = analysis.get("summary", "")

                if summary:
                    print(f"✅ Analysis ready! Summary: {summary[:100]}...")
                    return summary
                else:
                    print("Call ended but analysis not yet ready, waiting...")
                    time.sleep(poll_interval)
                    continue

            # Call still in progress - continue waiting
            if status in ["scheduled", "ringing", "in-progress", "queued"]:
                print(f"Call still {status}, waiting...")
                time.sleep(poll_interval)
                continue
            
            # Unknown status - log and continue
            print(f"Unknown call status: {status}, continuing to wait...")
            time.sleep(poll_interval)

        print(f"⏱️ Timeout waiting for call analysis after {timeout_seconds}s")
        print(f"   Call may still be in progress. Analysis will be available later.")
        return None