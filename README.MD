# 🏠 YooseAI Algarve - AI-Powered Agentic Housing Workflow

<div align="center">

**Transform your housing search from weeks of frustration into minutes of intelligent automation**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🌟 What is YooseAI Algarve?

**YooseAI Algarve** is not just a chatbot; it's a sophisticated, multi-agent AI workflow designed to automate and revolutionize the search for long-term rental housing in Portugal's Algarve region.

Users interact with the system using natural language, specifying their ideal home. Our autonomous agent workforce then scours the entire internet, identifies the best properties, enriches the data with geospatial intelligence, and asynchronously initiates negotiation calls to landlords to determine availability and the best possible price. The result is a curated, actionable list of the best housing options, complete with negotiation intelligence—all delivered in **Portuguese**.

### 🎯 Key Differentiators

- 🤖 **Multi-Agent Architecture**: Specialized AI agents work in harmony to accomplish complex tasks
- 🌐 **Internet-Wide Search**: Aggregates listings from all major Portuguese real estate portals
- 📞 **Automated Negotiation**: AI-powered phone calls handle initial landlord conversations
- 🇵🇹 **Portuguese-First**: Fully localized for the Algarve market
- 🗺️ **Geospatial Intelligence**: Maps, POIs, and neighborhood insights
- ⚡ **Asynchronous Processing**: Multiple properties researched and negotiated simultaneously

---

## 🔄 Core Workflow: From Text to Tenancy

This platform transforms a simple text-based request into a comprehensive, pre-negotiated housing portfolio.

### Step-by-Step Journey

```
┌─────────────────────────────────────────────────────────────────┐
│  "Olá, procuro um apartamento T2 em Faro perto da universidade, │
│   até 1000€. Tenho um cão pequeno."                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🔍 Internet-Wide Search & Aggregation                          │
│  • Idealista, Imovirtual, Casa Sapo, OLX                        │
│  • Intelligent de-duplication                                   │
│  • Structured data extraction                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🎯 Intelligent Selection & Enrichment                          │
│  • Compatibility scoring against user profile                   │
│  • Geocoded coordinates                                         │
│  • Local POIs (supermarkets, schools, transport)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  📞 Automated, Asynchronous Negotiation Calls                  │
│  • Pre-call intelligence gathering                              │
│  • AI-powered phone calls to landlords                          │
│  • Natural Portuguese conversations                             │
│  • Availability & price flexibility inquiries                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ✨ Curated, Actionable Results                                 │
│  • Best options with negotiation insights                      │
│  • Availability confirmations                                   │
│  • Price negotiation outcomes                                   │
│  • Ready-to-contact listings                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 1️⃣ Natural Language Input

A user simply describes what they're looking for in Portuguese:

> **Example**: *"Olá, procuro um apartamento T2 em Faro perto da universidade, até 1000€. Tenho um cão pequeno."*

The system understands:
- Property type (T2 apartment)
- Location (Faro, near university)
- Budget constraint (up to €1000)
- Special requirements (small dog allowed)

### 2️⃣ Internet-Wide Search & Aggregation

The **Research Agent** is dispatched to query all major real estate portals:

- **Idealista** - Portugal's leading property portal
- **Imovirtual** - Comprehensive listing database
- **Casa Sapo** - Popular marketplace
- **OLX Imóveis** - Classified ads platform

It gathers every potential match, intelligently de-duplicates listings using URL fingerprints and address normalization, and structures the raw data into a consistent format.

### 3️⃣ Intelligent Selection & Enrichment

The system filters the aggregated list, scoring each property for compatibility against the user's profile. It enriches each valid listing with:

- **Geocoded coordinates** via Mapbox
- **Local points of interest** (POIs):
  - 🏫 Schools and universities
  - 🛒 Supermarkets and shopping
  - 🏥 Healthcare facilities
  - 🚌 Public transport stops
  - 🏖️ Beaches and recreation
- **Negotiation scoring** based on market conditions

### 4️⃣ Automated, Asynchronous Negotiation Calls

This is where **YooseAI Algarve** truly shines. The user can select their top properties, and the system initiates the VAPI Agent workflow:

1. **Prober Agent** gathers pre-call intelligence:
   - Time on market
   - Price history and reductions
   - Property characteristics
   - Market comparisons

2. **VAPI Agent** places asynchronous, AI-powered phone calls:
   - Converses naturally in Portuguese
   - Confirms availability
   - Inquires about price flexibility
   - Understands specific tenant requirements
   - Extracts key negotiation points

3. **LLM Analyzer** processes call transcripts:
   - Extracts availability status
   - Identifies negotiation opportunities
   - Summarizes landlord responses

### 5️⃣ Curated, Actionable Results

The user is presented with a final, distilled list of the best options. Each listing is now augmented with:

- ✅ Availability confirmations
- 💰 Price negotiation outcomes
- 📝 Landlord response summaries
- 🎯 Negotiation intelligence
- 📍 Enriched location data

---

## 🏗️ System Architecture: An Orchestra of Agents

YooseAI Algarve is built on a robust, microservices-inspired architecture where specialized AI agents collaborate to fulfill the user's goal. This multi-agent system is orchestrated by a central Coordinator and exposed via a FastAPI REST API.

### High-Level Agentic Workflow

#### Phase 1: Research & Enrichment

```
[User Defines Housing Need via Text]
    ↓ (Natural Language Request)
[FastAPI / Coordinator]
    ↓ (Parse & Structure)
[Scoping Agent - Understands the Query]
    ↓ (UserRequirements Schema)
[FastAPI / Coordinator]
    ↓ (Search Query)
[Research Agent - Searches the Internet]
    ↓ (HTTP Requests)
[Real Estate Portals: Idealista, Imovirtual, Casa Sapo, OLX]
    ↓ (Listing Data)
[Research Agent]
    ↓ (PropertyListings)
[FastAPI / Coordinator]
    ↓ (Enrichment Tasks)
[Enrichment Agents - Mapbox, POIs, Scoring]
    ↓ (API Calls)
[Mapping & Data APIs: Mapbox, Geocoding, POIs]
    ↓ (Geocoded Data & POIs)
[Enrichment Agents]
    ↓ (Enriched Listings)
[FastAPI / Coordinator]
```

#### Phase 2: Automated Negotiation (Asynchronous)

```
[FastAPI / Coordinator]
    ↓ (Selected Properties)
[Prober Agent - Gathers Negotiation Intel]
    ↓ (Web Research)
[Real Estate Portals]
    ↓ (Negotiation Intel)
[FastAPI / Coordinator]
    ↓ (Call Configuration)
[VAPI Agent - Places AI Phone Calls]
    ↓ (Phone Calls)
[Telephony Service: VAPI - AI Phone Calls]
    ↓ (Call Transcripts)
[VAPI Agent]
    ↓ (Analysis Request)
[LLM Analyzer - Extracts Call Outcomes]
    ↓ (Structured Outcomes)
[FastAPI / Coordinator]
    ↓ (Final Results)
[User Receives Curated List with Negotiation Insights]
```

#### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
│  [1. User Defines Housing Need via Text]                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI / COORDINATOR                         │
│              (Orchestrates Agent Workflow)                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 1: RESEARCH & ENRICHMENT                      │
│                                                                  │
│  [Scoping Agent] → [Research Agent] → [Enrichment Agents]      │
│  • Understands Query    • Searches Internet   • Mapbox, POIs   │
│  • Extracts Requirements • Aggregates Data      • Scoring        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                              │
│                                                                  │
│  [Real Estate Portals]      [Mapping APIs]                      │
│  • Idealista                 • Mapbox                            │
│  • Imovirtual                • Geocoding                         │
│  • Casa Sapo                 • POIs                              │
│  • OLX                                                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 2: AUTOMATED NEGOTIATION                      │
│                    (Asynchronous)                                │
│                                                                  │
│  [Prober Agent] → [VAPI Agent] → [LLM Analyzer]                 │
│  • Gathers Intel     • Places Calls     • Extracts Outcomes     │
│  • Market Research   • Negotiates Price  • Structures Results    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                              │
│                                                                  │
│  [Telephony Service: VAPI - AI Phone Calls]                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                              │
│  [8. Presents Curated List with Negotiation Insights]           │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Roles & Responsibilities

Each agent is a specialized worker with a clear role in the assembly line:

#### 🎯 Coordinator Agent (`main.py`)
The **project manager**. It receives requests from the API and directs tasks to the appropriate specialist agents, ensuring the workflow proceeds smoothly and results are aggregated correctly.

**Key Responsibilities:**
- Routes requests to appropriate agents
- Aggregates responses from multiple agents
- Manages session state
- Handles error recovery and fallbacks

#### 💬 Scoping Agent (`scoping_agent.py`)
The **conversational specialist**. It interprets the user's natural language request and transforms it into a structured `UserRequirements` schema that other agents can act upon.

**Key Responsibilities:**
- Natural language understanding
- Extracts requirements: budget, location, bedrooms, amenities
- Handles follow-up questions
- Validates completeness of requirements

**Example Output:**
```python
UserRequirements(
    budget_min=800,
    budget_max=1000,
    bedrooms=2,
    location="Faro",
    additional_info="Near university, small dog allowed"
)
```

#### 🔍 Research Agent (`research_agent.py`)
The **tireless data miner**. It queries multiple online sources, scrapes listing data using BrightData and Firecrawl, and cleans the results.

**Key Responsibilities:**
- Multi-source web scraping
- Data extraction and normalization
- De-duplication logic
- Quality filtering

**Supported Sources:**
- Idealista.pt
- Imovirtual.com
- Casasapo.pt
- OLX.pt

#### 🕵️ Prober Agent (`prober_agent.py`)
The **private investigator**. Before a call is made, this agent scours the web for any information that could provide negotiation leverage.

**Key Responsibilities:**
- Price history research
- Time-on-market analysis
- Comparable property research
- Market condition assessment

**Example Findings:**
- Property listed for 3 months
- Price reduced by €50/month
- Similar properties in area priced lower
- High availability in neighborhood

#### 📞 VAPI Agent (`vapi_agent.py`)
The **negotiator**. This agent uses the VAPI service to conduct AI-powered, human-like phone calls. It is dynamically configured with the property details and negotiation points from the Prober Agent to achieve its objectives.

**Key Responsibilities:**
- Initiates asynchronous phone calls
- Converses naturally in Portuguese
- Confirms availability
- Negotiates price flexibility
- Gathers tenant requirements

**Call Objectives:**
- ✅ Confirm property availability
- 💰 Inquire about price flexibility
- 📅 Understand move-in timeline
- 📋 Clarify tenant requirements
- 🏠 Gather property details

#### 🗺️ Mapbox Agent (`mapbox_agent.py`)
The **geospatial specialist**. Enriches property listings with precise coordinates and location intelligence.

**Key Responsibilities:**
- Geocoding addresses
- Reverse geocoding coordinates
- POI discovery
- Route calculations

#### 🏘️ Local Discovery Agent (`local_agent.py`)
The **neighborhood expert**. Discovers and analyzes local amenities and points of interest.

**Key Responsibilities:**
- Find nearby schools
- Locate supermarkets
- Identify public transport
- Map healthcare facilities

#### 👥 Community Analysis Agent (`community_agent.py`)
The **neighborhood analyst**. Provides insights about the local community and area characteristics.

**Key Responsibilities:**
- Demographic analysis
- Safety indicators
- Community amenities
- Area reputation

---

## 📊 Core Schemas: The Blueprint for Success

A reliable agentic workflow depends on structured, predictable data models. Our core schemas ensure that information flows consistently between agents, preventing errors and ensuring each agent has the context it needs to perform its task.

All data models are defined using **Pydantic** in `backend/models.py`.

### Key Schemas

#### `UserRequirements`
A structured representation of the user's needs.

```python
class UserRequirements(Model):
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    location: str
    additional_info: Optional[str] = None
```

#### `PropertyListing`
A normalized model for a housing property, containing all enriched data.

```python
class PropertyListing(Model):
    address: Optional[str] = None
    city: Optional[str] = None
    price: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    negotiation_score: Optional[float] = None
    contact_phone: Optional[str] = None
    url: Optional[str] = None
    # ... and more
```

#### `ProberFinding`
A piece of actionable intelligence found by the Prober Agent.

```python
class ProberFinding(Model):
    finding_type: str  # e.g., "price_reduction", "time_on_market"
    description: str
    confidence: float
    source_url: Optional[str] = None
```

#### `VapiRequest` / `VapiResponse`
The data packets for initiating and reporting on automated phone calls.

```python
class VapiRequest(Model):
    property_address: str
    listing_url: str
    contact_phone: str
    user_name: str
    user_email: str
    prober_findings: List[ProberFinding]
    # ... call configuration

class VapiResponse(Model):
    call_id: str
    status: str
    transcript: Optional[str] = None
    availability: Optional[bool] = None
    price_flexibility: Optional[str] = None
    # ... call outcomes
```

---

## 📁 Repository Structure

The project is organized to separate concerns, making it easy to navigate, maintain, and extend.

```
Algarve_Hack/
├── backend/                          # Python backend - Agent orchestration
│   ├── api.py                        # FastAPI server for the negotiation workflow
│   ├── main.py                       # Main entry point with Coordinator Agent
│   ├── models.py                     # Core Pydantic data models and schemas
│   ├── llm_client.py                 # Shared client for interacting with LLMs
│   ├── requirement.txt               # Python dependencies
│   │
│   ├── agents/                       # Specialized AI agents
│   │   ├── base_agent.py             # Base agent utilities
│   │   ├── scoping_agent.py          # Natural language understanding
│   │   ├── research_agent.py         # Web scraping and aggregation
│   │   ├── prober_agent.py           # Pre-call intelligence gathering
│   │   ├── vapi_agent.py             # AI phone call orchestration
│   │   ├── vapi_prompts.py           # Portuguese call prompts
│   │   ├── mapbox_agent.py           # Geocoding and mapping
│   │   ├── local_agent.py            # POI discovery
│   │   └── community_agent.py        # Neighborhood analysis
│   │
│   ├── clients/                      # External API clients
│   │   ├── brigthdata.py             # Bright Data scraping services
│   │   ├── firecrawl_mcp.py          # Firecrawl scraping services
│   │   ├── tavily.py                 # Tavily search API
│   │   └── vapi.py                   # Low-level VAPI telephony API
│   │
│   └── utils/                        # Utility functions
│       ├── scraper.py                # HTML parsing utilities
│       └── firecrawl_scraper.py      # Firecrawl integration helpers
│
├── frontend/                         # Next.js frontend
│   ├── app/                          # Next.js app directory
│   │   ├── components/               # React components
│   │   │   ├── ChatInterface.tsx     # Main chat UI
│   │   │   ├── MapView.tsx           # Interactive map display
│   │   │   ├── PropertyCard.tsx      # Property listing cards
│   │   │   └── ...                   # Other UI components
│   │   ├── sections/                 # Page sections
│   │   ├── services/                 # API client services
│   │   └── types/                    # TypeScript type definitions
│   ├── package.json                  # Node.js dependencies
│   └── tsconfig.json                 # TypeScript configuration
│
├── tests/                            # Test suite
│   ├── test_search_flow.py           # Integration tests
│   └── test_direct_vapi_call.py      # VAPI call tests
│
├── README.MD                         # This file
├── PRD.MD                            # Product Requirements Document
└── LICENSE                           # MIT License
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **Active API Keys** for:
  - ASI or another LLM provider (`ASI_API_KEY`)
  - Bright Data (`BRIGHT_DATA_API_KEY`)
  - Firecrawl (`FIRECRAWL_API_KEY`)
  - VAPI (`VAPI_PRIVATE_API_KEY`, `VAPI_ASSISTANT_ID`, `VAPI_PHONE_NUMBER_ID`)
  - Mapbox (`MAPBOX_API_KEY`)

### Installation & Setup

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Algarve_Hack
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirement.txt

# Create environment file
cp .env.example .env  # If exists, or create manually
```

#### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# LLM Configuration
ASI_API_KEY="sk-..."

# Web Scraping Services
BRIGHT_DATA_API_KEY="..."
FIRECRAWL_API_KEY="..."

# VAPI Telephony Service
VAPI_PRIVATE_API_KEY="..."
VAPI_ASSISTANT_ID="..."
VAPI_PHONE_NUMBER_ID="..."

# Mapping & Geocoding
MAPBOX_API_KEY="pk.eyJ..."

# Optional: Tavily Search
TAVILY_API_KEY="..."
```

#### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Create environment file (if needed)
cp .env.example .env.local
```

#### 5. Run the Application

**Start the Backend (Agent Bureau):**

```bash
# From backend directory
python backend/main.py
```

The FastAPI server will be available at `http://localhost:8080`, with endpoints like:
- `/api/chat` - Main chat endpoint
- `/api/negotiate` - Negotiation workflow endpoint

**Start the Frontend:**

```bash
# From frontend directory
npm run dev
```

The Next.js app will be available at `http://localhost:3000`

---

## 🔌 API Endpoints

### Chat Endpoint

**POST** `/api/chat`

Initiates a conversation with the agent system.

```json
{
  "message": "Procuro um T2 em Faro até 1000€",
  "session_id": "unique-session-id"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "response": "Encontrei 15 propriedades que correspondem aos seus critérios...",
    "properties": [...],
    "session_id": "unique-session-id"
  }
}
```

### Negotiate Endpoint

**POST** `/api/negotiate`

Initiates automated negotiation calls for selected properties.

```json
{
  "address": "Rua da Universidade, Faro",
  "name": "João Silva",
  "email": "joao@example.com",
  "additional_info": "Interested in viewing",
  "listing_data": {
    "contact_phone": "+351912345678",
    "price": 950,
    "title": "T2 Apartment near University"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "call_id": "vapi-call-id",
  "message": "Call initiated successfully"
}
```

---

## 🧪 Testing

Run the test suite:

```bash
# From project root
cd tests
python -m pytest test_search_flow.py
python -m pytest test_direct_vapi_call.py
```

---

## 🛠️ Technology Stack

### Backend
- **uAgents** - Multi-agent framework
- **FastAPI** - REST API framework
- **Pydantic** - Data validation and settings
- **Python 3.10+** - Runtime

### Frontend
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React 19** - UI library

### External Services
- **Bright Data** - Web scraping infrastructure
- **Firecrawl** - Web scraping service
- **VAPI** - AI telephony platform
- **Mapbox** - Mapping and geocoding
- **Tavily** - Search API

---

## 📈 Performance & Scalability

- **Chat Response Time**: p95 < 3 seconds
- **Geocoding & POI**: Batch processing < 6 seconds
- **Scraping Rate**: ≤ 2 requests per second per domain
- **Concurrent Calls**: Asynchronous VAPI calls handle multiple properties simultaneously

---

## 🔒 Security & Privacy

- **GDPR Compliant**: Explicit consent for data processing
- **Data Minimization**: Only necessary data collected
- **Secure Storage**: API keys stored in environment variables
- **Rate Limiting**: Respects source website ToS

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Portuguese real estate portals for providing listing data
- VAPI for AI telephony capabilities
- Mapbox for geospatial services
- The uAgents community

---

## 📞 Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ for the Algarve housing community**

Made in Portugal 🇵🇹

</div>

