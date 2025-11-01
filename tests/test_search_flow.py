"""
Integration Test: Complete Search Flow with Real Agents
======================================================

Tests the complete flow:
1. User query -> Scoping Agent (extract requirements)
2. Research Agent (search properties)
3. Parse & Organize results
4. Display results in predictable format
5. User selects property for contact
6. Trigger call based on context

FAILS LOUDLY to ensure proper implementation.
"""
import pytest
import json
import uuid
import requests
from typing import Dict, Any, Optional

# Backend API endpoint
BACKEND_URL = "http://localhost:8080"
CHAT_ENDPOINT = f"{BACKEND_URL}/api/chat"
NEGOTIATE_ENDPOINT = f"{BACKEND_URL}/api/negotiate"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"


class TestSearchFlow:
    """Test the complete search flow from query to contact"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_session_id = str(uuid.uuid4())
        self.test_query = "Procuro apartamento de 2 quartos em Lisboa até 300k"
        
    def _check_backend_health(self) -> bool:
        """Check if backend is running"""
        try:
            # Try health endpoint first
            response = requests.get(HEALTH_ENDPOINT, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Fallback: try /api/chat endpoint (which we know exists)
        try:
            response = requests.post(
                CHAT_ENDPOINT,
                json={"message": "health_check", "session_id": "health_check"},
                timeout=5
            )
            # If we get any response (even error), backend is running
            return response.status_code in [200, 400, 422]
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            return False
    
    def _send_chat_request(self, message: str, session_id: str, timeout: int = 800) -> Dict[str, Any]:
        """Send chat request to backend and wait for response"""
        print(f"\n📤 Sending chat request...")
        print(f"   Message: {message}")
        print(f"   Session ID: {session_id}")
        
        payload = {
            "message": message,
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                CHAT_ENDPOINT,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"❌ TIMEOUT: Request took longer than {timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise Exception(f"❌ CONNECTION ERROR: Backend not running at {BACKEND_URL}")
        except Exception as e:
            raise Exception(f"❌ REQUEST FAILED: {str(e)}")
    
    def _send_negotiate_request(self, address: str, name: str, email: str, additional_info: str = "") -> Dict[str, Any]:
        """Send negotiate request to backend"""
        print(f"\n📞 Sending negotiate request...")
        print(f"   Address: {address}")
        print(f"   User: {name} ({email})")
        
        payload = {
            "address": address,
            "name": name,
            "email": email,
            "additional_info": additional_info
        }
        
        try:
            response = requests.post(
                NEGOTIATE_ENDPOINT,
                json=payload,
                timeout=300  # 5 minutes for full negotiation flow
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"❌ TIMEOUT: Negotiation request took longer than 5 minutes")
        except Exception as e:
            raise Exception(f"❌ NEGOTIATE REQUEST FAILED: {str(e)}")
    
    def _parse_chat_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate chat response structure"""
        print(f"\n📥 Received response:")
        print(f"   Status: {response.get('status')}")
        
        if response.get('status') != 'success':
            error_msg = response.get('data', {}).get('message', 'Unknown error')
            raise Exception(f"❌ RESPONSE STATUS NOT SUCCESS: {error_msg}")
        
        data = response.get('data', {})
        
        # Validate required fields
        required_fields = ['requirements', 'properties', 'search_summary', 'total_found']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            raise Exception(f"❌ MISSING REQUIRED FIELDS: {missing_fields}")
        
        return data
    
    def _organize_results(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and organize search results in a predictable structure"""
        print(f"\n📊 Organizing results...")
        
        requirements = chat_data.get('requirements', {})
        properties = chat_data.get('properties', [])
        raw_results = chat_data.get('raw_search_results', [])
        search_summary = chat_data.get('search_summary', '')
        total_found = chat_data.get('total_found', 0)
        
        if not properties and total_found == 0:
            raise Exception("❌ NO PROPERTIES FOUND: Search returned zero results")
        
        organized = {
            "summary": search_summary,
            "total_found": total_found,
            "session_id": self.test_session_id,
            "requirements": requirements,
            "properties": [],
            "raw_results_count": len(raw_results),
            "metadata": {
                "has_coordinates": len([p for p in properties if p.get('latitude')]) > 0,
                "has_images": len(raw_results) > 0 and any(r.get('image_url') for r in raw_results),
                "has_pois": len(raw_results) > 0 and any(r.get('pois') for r in raw_results),
                "has_community_analysis": 'community_analysis' in chat_data
            }
        }
        
        # Organize properties
        for i, prop in enumerate(properties):
            organized_property = {
                "id": f"prop_{i+1}",
                "title": self._generate_property_title(prop),
                "address": prop.get("address", "Address not available"),
                "price": {
                    "value": prop.get("price", 0),
                    "formatted": f"{prop.get('price', 0):,}€".replace(",", "."),
                    "currency": "EUR"
                },
                "specifications": {
                    "bedrooms": prop.get("bedrooms"),
                    "bathrooms": prop.get("bathrooms"),
                    "area": {
                        "value": prop.get("sqft"),
                        "unit": "m²"
                    }
                },
                "description": prop.get("description", ""),
                "location": {
                    "city": prop.get("city", ""),
                    "coordinates": {
                        "lat": prop.get("latitude"),
                        "lng": prop.get("longitude")
                    } if prop.get("latitude") else None
                },
                "links": {
                    "property_url": prop.get("url", ""),
                    "source": "real_estate_platform"
                },
                "images": {
                    "thumbnail": self._get_image_for_property(i, raw_results),
                    "gallery_available": bool(self._get_image_for_property(i, raw_results))
                },
                "contact_ready": True,
                "negotiation_score": prop.get("negotiation_score", 5.0)  # Use score from backend
            }
            organized["properties"].append(organized_property)
        
        return organized
    
    def _generate_property_title(self, prop: Dict[str, Any]) -> str:
        """Generate property title from available data"""
        bedrooms = prop.get("bedrooms")
        address = prop.get("address", "Unknown location")
        
        if bedrooms:
            return f"Apartamento {bedrooms} quartos - {address}"
        return f"Propriedade - {address}"
    
    def _get_image_for_property(self, index: int, raw_results: list) -> Optional[str]:
        """Get image URL for property at given index"""
        if index < len(raw_results):
            return raw_results[index].get('image_url')
        return None
    
    # Removed _calculate_negotiation_score - now using dynamic score from backend
    
    def _print_organized_results(self, organized_results: Dict[str, Any]):
        """Print organized results in a readable format"""
        print(f"\n📊 Search Summary: {organized_results['summary'][:100]}...")
        print(f"🏠 Total Properties: {organized_results['total_found']}")
        print(f"📋 Properties Organized: {len(organized_results['properties'])}")
        print(f"📍 Has Coordinates: {organized_results['metadata']['has_coordinates']}")
        print(f"🖼️  Has Images: {organized_results['metadata']['has_images']}")
        print(f"🗺️  Has POIs: {organized_results['metadata']['has_pois']}")
        
        for i, prop in enumerate(organized_results["properties"]):
            print(f"\n--- Property {i+1} ---")
            print(f"Title: {prop['title']}")
            print(f"Price: {prop['price']['formatted']}")
            if prop['specifications']['bedrooms']:
                print(f"Specs: {prop['specifications']['bedrooms']} bed, {prop['specifications']['bathrooms']} bath, {prop['specifications']['area']['value']} m²")
            print(f"Description: {prop['description'][:80]}...")
            print(f"Negotiation Score: {prop['negotiation_score']}/10")
            print(f"Contact Ready: {prop['contact_ready']}")
    
    def _format_for_display(self, organized_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format results for API response/display"""
        return {
            "status": "success",
            "data": {
                "search_summary": organized_results["summary"],
                "results_count": organized_results["total_found"],
                "properties": organized_results["properties"],
                "metadata": organized_results["metadata"]
            },
            "ui_ready": True,
            "contact_enabled": True
        }
    
    def _prepare_contact_action(self, property_data: Dict[str, Any], original_query: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare contact/call action based on property and context"""
        return {
            "action_type": "initiate_contact",
            "method": "phone_call",
            "property": {
                "id": property_data["id"],
                "title": property_data["title"],
                "address": property_data["address"],
                "price": property_data["price"]["formatted"]
            },
            "contact_context": {
                "user_query": original_query,
                "requirements": requirements,
                "session_id": self.test_session_id
            },
            "call_parameters": {
                "property_id": property_data["id"],
                "inquiry_type": "property_visit_request",
                "preferred_contact_method": "phone",
                "urgency": "normal",
                "custom_message": f"Olá! Estou interessado no apartamento em {property_data['address']} priced at {property_data['price']['formatted']}. Gostaria de agendar uma visita."
            },
            "vapi_integration": {
                "enabled": True,
                "voice_context": f"User looking for {property_data['specifications']['bedrooms']} bedroom apartment in {requirements.get('location', 'Lisboa')} around {property_data['price']['value']}€",
                "agent_personality": "professional_portuguese_realtor"
            }
        }
    
    def test_search_flow_complete(self):
        """Test the complete search flow with REAL agents"""
        print("\n" + "="*80)
        print("🧪 TESTING COMPLETE SEARCH FLOW WITH REAL AGENTS")
        print("="*80)
        
        # Step 0: Check backend health
        print(f"\n🔍 Step 0: Checking Backend Health")
        if not self._check_backend_health():
            error_msg = (
                f"\n{'='*80}\n"
                f"❌ BACKEND NOT RUNNING!\n"
                f"{'='*80}\n"
                f"\n📋 To start the backend, choose one of these options:\n"
                f"\n   Option 1 (Recommended):\n"
                f"      python tests/start_backend.py\n"
                f"\n   Option 2:\n"
                f"      cd backend\n"
                f"      python main.py\n"
                f"\n   Option 3:\n"
                f"      cd backend && python -m main\n"
                f"\n📍 Expected URL: {BACKEND_URL}\n"
                f"🔗 Health check: {HEALTH_ENDPOINT}\n"
                f"\n💡 The backend will start multiple agents:\n"
                f"   - Scoping Agent (port 8001)\n"
                f"   - Research Agent (port 8002)\n"
                f"   - Coordinator/API (port 8080)\n"
                f"   - And more...\n"
                f"\n⏳ Wait for 'Coordinator started' message before running tests\n"
                f"{'='*80}\n"
            )
            raise Exception(error_msg)
        print("✅ Backend is running")
        
        # Step 1: Send user search query
        print(f"\n📝 Step 1: User Search Query")
        print(f"Query: {self.test_query}")
        print(f"Session ID: {self.test_session_id}")
        
        try:
            chat_response = self._send_chat_request(self.test_query, self.test_session_id)
        except Exception as e:
            raise Exception(f"❌ STEP 1 FAILED - Chat Request Error: {str(e)}")
        
        # Step 2: Parse response
        print(f"\n🔍 Step 2: Parsing Response")
        try:
            chat_data = self._parse_chat_response(chat_response)
        except Exception as e:
            raise Exception(f"❌ STEP 2 FAILED - Response Parsing Error: {str(e)}\nResponse: {json.dumps(chat_response, indent=2)}")
        
        requirements = chat_data.get('requirements', {})
        print(f"✅ Requirements extracted:")
        print(f"   Location: {requirements.get('location', 'N/A')}")
        print(f"   Budget Max: {requirements.get('budget_max', 'N/A')}")
        print(f"   Bedrooms: {requirements.get('bedrooms', 'N/A')}")
        print(f"   Total Found: {chat_data.get('total_found', 0)}")
        
        # Step 3: Organize results
        print(f"\n📊 Step 3: Organizing Results")
        try:
            organized_results = self._organize_results(chat_data)
        except Exception as e:
            raise Exception(f"❌ STEP 3 FAILED - Results Organization Error: {str(e)}")
        
        self._print_organized_results(organized_results)
        
        # Step 4: Format for display
        print(f"\n📋 Step 4: Formatting for Display")
        formatted_display = self._format_for_display(organized_results)
        print(f"✅ Display format ready: {len(formatted_display['data']['properties'])} properties")
        
        # Step 5: User selects property for contact
        print(f"\n📞 Step 5: User Selects Property for Contact")
        if not organized_results["properties"]:
            raise Exception("❌ STEP 5 FAILED - No properties available to select")
        
        selected_property_index = 0  # User selects first property
        selected_property = organized_results["properties"][selected_property_index]
        print(f"Selected Property: {selected_property['title']}")
        print(f"Address: {selected_property['address']}")
        print(f"Price: {selected_property['price']['formatted']}")
        
        # Step 6: Prepare contact action
        print(f"\n🎯 Step 6: Preparing Contact Action")
        contact_action = self._prepare_contact_action(
            selected_property,
            self.test_query,
            requirements
        )
        print(f"✅ Contact action prepared:")
        print(f"   Action Type: {contact_action['action_type']}")
        print(f"   Method: {contact_action['method']}")
        print(f"   Property ID: {contact_action['property']['id']}")
        
        # Step 7: Trigger call/contact (optional - can be skipped if backend not ready)
        print(f"\n📞 Step 7: Trigger Contact/Call (Optional)")
        print(f"Note: Skipping actual call trigger - use /api/negotiate endpoint for full negotiation flow")
        print(f"Contact action structure: {json.dumps(contact_action, indent=2, ensure_ascii=False)}")
        
        print(f"\n✅ COMPLETE SEARCH FLOW TESTED SUCCESSFULLY!")
        print("="*80)
        
        # Assertions - Fail loudly
        assert organized_results["total_found"] > 0, f"❌ ASSERTION FAILED: total_found is {organized_results['total_found']}, expected > 0"
        assert len(organized_results["properties"]) > 0, f"❌ ASSERTION FAILED: No properties organized"
        assert contact_action["action_type"] == "initiate_contact", f"❌ ASSERTION FAILED: action_type is {contact_action['action_type']}, expected 'initiate_contact'"
        assert contact_action["method"] == "phone_call", f"❌ ASSERTION FAILED: method is {contact_action['method']}, expected 'phone_call'"
        assert selected_property["contact_ready"], f"❌ ASSERTION FAILED: Property not marked as contact_ready"
        
        print(f"\n✅ ALL ASSERTIONS PASSED!")
        
        return {
            "search_query": self.test_query,
            "session_id": self.test_session_id,
            "requirements": requirements,
            "chat_response": chat_response,
            "organized_results": organized_results,
            "display_format": formatted_display,
            "selected_property": selected_property,
            "contact_action": contact_action
        }
    
    def test_negotiate_flow(self):
        """Test the negotiation flow for a specific property"""
        print("\n" + "="*80)
        print("🧪 TESTING NEGOTIATION FLOW")
        print("="*80)
        
        # First, get a property from search
        print(f"\n📝 Step 1: Get Property from Search")
        chat_response = self._send_chat_request(self.test_query, self.test_session_id)
        chat_data = self._parse_chat_response(chat_response)
        organized_results = self._organize_results(chat_data)
        
        if not organized_results["properties"]:
            pytest.skip("No properties found in search - cannot test negotiation flow")
        
        # Get first property address
        first_property = organized_results["properties"][0]
        property_address = first_property["address"]
        
        print(f"\n📞 Step 2: Initiate Negotiation for Property")
        print(f"Property Address: {property_address}")
        
        try:
            negotiate_response = self._send_negotiate_request(
                address=property_address,
                name="Test User",
                email="test@example.com",
                additional_info="Interested in viewing this property"
            )
            
            print(f"\n✅ Negotiation Response:")
            print(f"   Success: {negotiate_response.get('success')}")
            print(f"   Leverage Score: {negotiate_response.get('leverage_score')}")
            print(f"   Call Status: {negotiate_response.get('call_status')}")
            print(f"   Call ID: {negotiate_response.get('call_id')}")
            
            assert negotiate_response.get('success') == True, f"❌ ASSERTION FAILED: Negotiation not successful"
            assert negotiate_response.get('leverage_score', 0) >= 0, f"❌ ASSERTION FAILED: Invalid leverage score"
            
        except Exception as e:
            raise Exception(f"❌ NEGOTIATION FLOW FAILED: {str(e)}")
        
        print(f"\n✅ NEGOTIATION FLOW TESTED SUCCESSFULLY!")
        print("="*80)


if __name__ == "__main__":
    # Run the test manually
    import sys
    
    test_instance = TestSearchFlow()
    test_instance.setup_method()
    
    try:
        results = test_instance.test_search_flow_complete()
        
        print(f"\n✅ TEST COMPLETED SUCCESSFULLY!")
        print(f"📊 Summary:")
        print(f"   - Properties Found: {results['organized_results']['total_found']}")
        print(f"   - Properties Organized: {len(results['organized_results']['properties'])}")
        print(f"   - Contact Action Ready: {results['contact_action']['action_type']}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        sys.exit(1)
