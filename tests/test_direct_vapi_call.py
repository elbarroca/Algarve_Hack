#!/usr/bin/env python3
"""
Test Direct VAPI Call - Bypass Prober Agent
============================================

This script demonstrates calling VAPI directly with detailed listing data,
skipping the slow prober agent research phase.

Usage:
1. Start backend: python backend/main.py
2. Run this script: python tests/test_direct_vapi_call.py

Optional environment variables:
- VAPI_TEST_PHONE: Phone number to call (required)
- VAPI_TEST_STUDENT_NAME: Student name (default: "Ricardo")
- VAPI_TEST_STUDENT_EMAIL: Student email (default: auto-generated)
- VAPI_TEST_ADDRESS: Property address (default: random from list)
- VAPI_TEST_PRICE: Property price in EUR (default: random)

Examples:
  VAPI_TEST_PHONE="+14722461622" python tests/test_direct_vapi_call.py
  VAPI_TEST_PHONE="+1234567890" VAPI_TEST_STUDENT_NAME="João" python tests/test_direct_vapi_call.py
"""

import requests
import json
import time
import os
import random
import sys
from typing import Dict, Any, Optional

# Configuration
API_URL = "http://localhost:8080/api/negotiate"

# Load .env file if it exists
def load_env_file() -> Dict[str, str]:
    """Load environment variables from .env file"""
    env_vars = {}
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

# Load .env variables
_env_vars = load_env_file()

# Realistic property addresses in Algarve, Portugal
ALGARVE_ADDRESSES = [
    "Rua da Oura 123, Albufeira, Algarve, Portugal",
    "Avenida Marginal, Praia da Rocha, Portimão, Algarve, Portugal",
    "Largo do Camões 45, Faro, Algarve, Portugal",
    "Rua do Comércio 12, Lagos, Algarve, Portugal",
    "Rua da Praia 78, Tavira, Algarve, Portugal",
    "Avenida dos Descobrimentos 234, Vila Real de Santo António, Algarve, Portugal",
    "Rua do Mar 56, Olhão, Algarve, Portugal",
    "Estrada da Praia 89, Carvoeiro, Lagoa, Algarve, Portugal"
]

# Realistic property types and descriptions
PROPERTY_TYPES = ["Apartment", "T2", "T3", "Studio", "House", "Villa"]
PROPERTY_DESCRIPTIONS = [
    "Modern apartment with sea view, fully furnished, modern kitchen, near beach and university",
    "Cozy 2-bedroom apartment in city center, recently renovated, ideal for students",
    "Bright apartment with balcony, close to public transport and university campus",
    "Furnished apartment in quiet neighborhood, walking distance to beach and shops",
    "Spacious apartment with large windows, modern amenities, perfect for student accommodation"
]

# Realistic student names (English-speaking)
STUDENT_NAMES = ["Ricardo", "John", "Maria", "Anna", "Peter", "Sophia", "Michael", "Emma"]

# Realistic amenities
AMENITIES_OPTIONS = [
    ["WiFi", "Air Conditioning", "Parking"],
    ["WiFi", "Parking", "Pool", "Gym"],
    ["WiFi", "Air Conditioning", "Balcony", "Sea View"],
    ["WiFi", "Parking", "Furnished", "Washing Machine"],
    ["WiFi", "Air Conditioning", "Parking", "Pool", "Gym", "Balcony"]
]


def get_env_or_default(key: str, default: Any = None) -> Optional[str]:
    """Get environment variable from .env file, then OS env, then default"""
    # First check .env file
    if key in _env_vars:
        return _env_vars[key]
    # Then check OS environment
    value = os.getenv(key)
    if value:
        return value
    # Finally return default
    return default


def generate_realistic_listing_data(
    contact_phone: Optional[str] = None,
    student_name: Optional[str] = None,
    student_email: Optional[str] = None,
    address: Optional[str] = None,
    price: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate realistic listing data for testing.
    Uses environment variables or generates random realistic data.
    """
    # Required: contact phone
    if not contact_phone:
        # Try VAPI_TEST_PHONE first, then VAPI_TARGET_PHONE from .env, then VAPI_MY_PHONE_NUMBER
        contact_phone = (
            get_env_or_default("VAPI_TEST_PHONE") or
            get_env_or_default("VAPI_TARGET_PHONE") or
            get_env_or_default("VAPI_MY_PHONE_NUMBER")
        )
        if not contact_phone:
            print("❌ ERROR: Phone number is required!")
            print("   Options:")
            print("   1. Set VAPI_TEST_PHONE environment variable")
            print("   2. Set VAPI_TARGET_PHONE in .env file (current: {})".format(
                _env_vars.get("VAPI_TARGET_PHONE", "not set")
            ))
            print("   3. Set VAPI_MY_PHONE_NUMBER in .env file")
            print("\n   Example: VAPI_TEST_PHONE='+14722461622' python tests/test_direct_vapi_call.py")
            sys.exit(1)
    
    # Student info
    if not student_name:
        student_name = get_env_or_default("VAPI_TEST_STUDENT_NAME", random.choice(STUDENT_NAMES))
    
    if not student_email:
        base_email = get_env_or_default("VAPI_TEST_STUDENT_EMAIL")
        if not base_email:
            # Generate realistic email from name (English format)
            base_email = f"{student_name.lower().replace(' ', '.')}@university.edu"
        student_email = base_email
    
    # Property address
    if not address:
        address = get_env_or_default("VAPI_TEST_ADDRESS", random.choice(ALGARVE_ADDRESSES))
    
    # Property price (realistic range for Algarve: 400-1500 EUR/month)
    if not price:
        price_str = get_env_or_default("VAPI_TEST_PRICE")
        if price_str:
            price = int(price_str)
        else:
            price = random.choice([450, 550, 650, 750, 850, 950, 1100, 1250, 1400])
    
    # Extract city from address
    city = address.split(',')[1].strip() if ',' in address else "Algarve"
    
    # Generate realistic property details
    property_type = random.choice(PROPERTY_TYPES)
    bedrooms = random.choice([1, 2, 3])
    bathrooms = max(1, bedrooms - 1) if bedrooms > 1 else 1
    sqft = random.choice([450, 550, 650, 750, 850, 950, 1100])
    description = random.choice(PROPERTY_DESCRIPTIONS)
    amenities = random.choice(AMENITIES_OPTIONS)
    
    # Realistic seller names
    seller_names = [
        "Algarve Properties Ltd",
        "Costa Real Estate",
        "Algarve Homes",
        "Portugal Properties",
        "Student Housing Algarve",
        "Rental Solutions PT"
    ]
    seller_name = random.choice(seller_names)
    
    # Generate realistic email from seller name
    seller_email = f"contact@{seller_name.lower().replace(' ', '').replace('ltd', '')}.pt"
    
    # Realistic availability dates
    availability_dates = [
        "September 1, 2025",
        "Available immediately",
        "January 2026",
        "Next month",
        "Flexible - discuss availability"
    ]
    
    # Additional info in English (to match English prompt)
    additional_info_options = [
        "I'm a university student looking for accommodation for the academic year. Interested in 2-bedroom apartments.",
        "Student looking for housing near the university. Need central location and easy access to public transport.",
        "I'm an international student looking for accommodation for next semester. Prefer furnished apartments.",
        "University student interested in long-term accommodation. Need space to study and location close to campus.",
        "I'm a student looking for shared or individual accommodation. Flexible budget depending on conditions."
    ]
    
    listing_data = {
        "address": address,
        "name": student_name,
        "email": student_email,
        "additional_info": random.choice(additional_info_options),
        "listing_data": {
            # Required fields
            "contact_phone": contact_phone,
            "price": price,
            "title": f"{property_type} in {city} - {bedrooms} Bedroom{'s' if bedrooms > 1 else ''}",
            
            # Recommended fields
            "description": description,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft": sqft,
            "property_type": property_type,
            "seller_name": seller_name,
            "seller_phone": contact_phone,  # Same as contact for simplicity
            "contact_email": seller_email,
            
            # Optional fields
            "amenities": amenities,
            "features": random.sample(["Balcony", "Sea View", "Furnished", "Terrace", "Garden"], 
                                    k=random.randint(1, 3)),
            "availability_date": random.choice(availability_dates),
            "lease_term": random.choice(["12 months minimum", "6 months minimum", "Flexible", "Long-term preferred"]),
            "utilities_included": random.choice([True, False]),
            "pets_allowed": random.choice([True, False]),
            "deposit_required": random.choice(["1 month rent", "2 months rent", "1.5 months rent"]),
            
            # Additional context
            "notes": random.choice([
                "Prefer long-term professional or student tenants. Property is in excellent condition.",
                "Recently renovated. Ideal for students or young professionals.",
                "Close to university campus and public transport. Quiet neighborhood.",
                "Fully furnished and ready to move in. All utilities available.",
                "Owner prefers students or professionals. Flexible lease terms available."
            ])
        }
    }
    
    return listing_data


def test_direct_vapi_call(listing_data: Optional[Dict[str, Any]] = None):
    """
    Test direct VAPI call with detailed listing data.
    
    Args:
        listing_data: Optional listing data dict. If None, will generate realistic data.
    """
    if listing_data is None:
        listing_data = generate_realistic_listing_data()
    
    print("=" * 70)
    print("🚀 Testing Direct VAPI Call (Bypassing Prober Agent)")
    print("=" * 70)
    print(f"\n📍 Property: {listing_data['address']}")
    print(f"👤 User: {listing_data['name']} (Student)")
    print(f"📧 Email: {listing_data['email']}")
    print(f"📞 Contact Phone: {listing_data['listing_data']['contact_phone']}")
    print(f"💰 Price: €{listing_data['listing_data']['price']}/month")
    print(f"🏠 Type: {listing_data['listing_data']['property_type']} - {listing_data['listing_data']['bedrooms']}BR/{listing_data['listing_data']['bathrooms']}BA")
    print(f"📏 Size: {listing_data['listing_data']['sqft']} sqft")
    print(f"🏢 Seller: {listing_data['listing_data']['seller_name']}")
    print(f"🗣️ Language: English (VAPI voice)")
    print(f"⚡ Will skip prober agent if contact_phone is provided")
    print("\n" + "=" * 70)

    try:
        print("\n📤 Sending POST request to negotiate endpoint...")
        print(f"URL: {API_URL}")
        print("⏱️  Expected to be FAST (no web scraping, straight to VAPI)")
        print("🇬🇧 Agent will speak in English (VAPI voice)")

        response = requests.post(
            API_URL,
            json=listing_data,
            timeout=180  # 3 minutes (should be much faster now)
        )

        print(f"\n📥 Response received!")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS!")
            print("=" * 70)

            # Extract data - response structure may vary
            if isinstance(result, dict) and 'data' in result:
                data = result.get('data', {})
            else:
                data = result

            print(f"Success: {data.get('success', result.get('success', False))}")
            print(f"Leverage Score: {data.get('leverage_score', result.get('leverage_score', 0))}/10")
            print(f"\n📝 Message:")
            print(f"   {data.get('message', result.get('message', 'N/A'))}")

            # Call summary
            call_summary = data.get('call_summary', result.get('call_summary', ''))
            if call_summary:
                print(f"\n📞 Call Summary:")
                print(f"   {call_summary[:300]}...")
                if len(call_summary) > 300:
                    print(f"   ... (truncated, full summary saved to file)")

            # Structured outcomes
            print("\n🎯 Structured Outcomes from VAPI Call:")
            print("=" * 70)

            availability = data.get('availability_date', result.get('availability_date'))
            if availability:
                print(f"✅ Availability: {availability}")
            else:
                print(f"⚠️  Availability: Not captured from call")

            price_flex = data.get('price_flexibility', result.get('price_flexibility'))
            if price_flex:
                print(f"✅ Price Flexibility: {price_flex}")
            else:
                print(f"⚠️  Price Flexibility: Not captured from call")

            tenant_req = data.get('tenant_requirements', result.get('tenant_requirements'))
            if tenant_req:
                print(f"✅ Tenant Requirements: {tenant_req}")
            else:
                print(f"⚠️  Tenant Requirements: Not captured from call")

            # Next actions
            next_actions = data.get('next_actions', result.get('next_actions', []))
            if next_actions:
                print(f"\n📋 Next Actions ({len(next_actions)}):")
                for idx, action in enumerate(next_actions, 1):
                    print(f"   {idx}. {action}")

            # Call status
            call_status = data.get('call_status', result.get('call_status', 'N/A'))
            call_id = data.get('call_id', result.get('call_id', 'N/A'))
            print(f"\n📞 Call Status:")
            print(f"   Status: {call_status}")
            print(f"   Call ID: {call_id}")

            print("\n" + "=" * 70)
            print("✅ Test completed successfully!")
            print("=" * 70)

            # Save full response
            output_file = "/tmp/direct_vapi_call_response.json"
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full response saved to: {output_file}")

            # Performance metrics
            print("\n⚡ Performance:")
            print("   - Skipped slow prober agent web scraping")
            print("   - Went straight to VAPI call with listing data")
            print("   - Much faster than full research flow")
            print("   - Agent speaks in English (VAPI voice)")

            return True

        else:
            print(f"\n❌ FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out!")
        print("Possible reasons:")
        print("  - VAPI call may still be in progress")
        print("  - Network issues")
        print("  - Server not responding")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection error: {e}")
        print("\nIs the backend server running?")
        print("Start it with: python backend/main.py")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_server_health():
    """Check if the server is running"""
    try:
        print("🏥 Checking server health...")
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"⚠️ Server returned status {response.status_code}")
            return False
    except:
        print("❌ Server is not reachable!")
        print("\nPlease start the backend server:")
        print("  cd backend")
        print("  python main.py")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 Direct VAPI Call Test - No Research, Just Phone Call")
    print("=" * 70)

    print("\n💡 This test demonstrates:")
    print("   1. Bypassing slow prober agent web scraping")
    print("   2. Providing detailed listing data directly")
    print("   3. Making immediate VAPI call to property agent")
    print("   4. Extracting structured outcomes (availability, price, tenant)")
    print("   5. Agent speaks in English (VAPI voice)")
    print("   6. Agent introduces as student looking for housing")

    print("\n⚙️  Configuration:")
    print("   Phone number sources (checked in order):")
    print("   1. VAPI_TEST_PHONE environment variable")
    print("   2. VAPI_TARGET_PHONE from .env file (current: {})".format(
        _env_vars.get("VAPI_TARGET_PHONE", "not set")
    ))
    print("   3. VAPI_MY_PHONE_NUMBER from .env file")
    print("\n   Optional environment variables:")
    print("   - VAPI_TEST_STUDENT_NAME: Student name (default: random)")
    print("   - VAPI_TEST_STUDENT_EMAIL: Student email (default: auto-generated)")
    print("   - VAPI_TEST_ADDRESS: Property address (default: random from Algarve)")
    print("   - VAPI_TEST_PRICE: Property price in EUR (default: random 400-1500)")

    print("\n⚠️  IMPORTANT:")
    print("   - Phone number is REQUIRED (from .env or environment variable)")
    print("   - The VAPI call will actually be placed to this number!")
    print("   - Agent will speak in English (VAPI voice)")
    print("   - Data is randomized for realistic testing")
    print("\n   Example usage:")
    print("   # Uses VAPI_TARGET_PHONE from .env by default:")
    print("   python tests/test_direct_vapi_call.py")
    print("\n   # Override with environment variable:")
    print("   VAPI_TEST_PHONE='+1234567890' VAPI_TEST_STUDENT_NAME='John' python tests/test_direct_vapi_call.py")

    time.sleep(2)

    # Check server health first
    if not check_server_health():
        exit(1)

    # Wait a moment
    time.sleep(1)

    # Generate realistic listing data
    print("\n🎲 Generating realistic test data...")
    listing_data = generate_realistic_listing_data()
    
    print(f"✅ Generated test data:")
    print(f"   Student: {listing_data['name']} ({listing_data['email']})")
    print(f"   Property: {listing_data['address']}")
    print(f"   Price: €{listing_data['listing_data']['price']}/month")
    print(f"   Type: {listing_data['listing_data']['property_type']}")
    print()

    # Run test
    success = test_direct_vapi_call(listing_data)

    # Exit with appropriate code
    exit(0 if success else 1)
