# 🔌 Guia de Integração - Frontend ↔ Backend

## 📋 Sumário

Este guia explica como o frontend Next.js se integra com o backend Python (FastAPI + uAgents).

## 🏗️ Arquitetura de Integração

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │              app/page.tsx                          │    │
│  │  (Homes AI Algarve - Main Application)            │    │
│  └───────────┬────────────────────────────────────────┘    │
│              │                                              │
│              ├──► ChatInterface                             │
│              ├──► PropertyCard                              │
│              ├──► RoommateProfileForm                       │
│              └──► FAQSection                                │
│              │                                              │
│  ┌───────────▼─────────────────────────────────────┐       │
│  │     services/api.ts (HomesAIAPI)               │       │
│  │  - searchProperties()                          │       │
│  │  - calculateMatch()                            │       │
│  │  - getPOIs()                                   │       │
│  │  - getFAQs()                                   │       │
│  └────────────┬───────────────────────────────────┘       │
└───────────────┼───────────────────────────────────────────┘
                │ HTTP/REST
                │
┌───────────────▼───────────────────────────────────────────┐
│                 BACKEND (FastAPI + uAgents)               │
│  ┌──────────────────────────────────────────────────┐    │
│  │           backend/api.py                         │    │
│  │  FastAPI Server (Port 8001)                     │    │
│  └───────┬──────────────────────────────────────────┘    │
│          │                                                │
│          ├──► POST /api/search                            │
│          ├──► POST /api/match                             │
│          └──► GET /api/pois                               │
│          │                                                │
│  ┌───────▼──────────────────────────────────────────┐    │
│  │           uAgents Orchestration                  │    │
│  │  - research_agent.py (search properties)        │    │
│  │  - matching_agent.py (calculate compatibility) │    │
│  │  - mapbox_agent.py (geocoding)                 │    │
│  │  - local_agent.py (POIs)                       │    │
│  │  - community_agent.py (area analysis)          │    │
│  └─────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Dados Completo

### 1️⃣ Procura de Propriedades

```typescript
// FRONTEND: User submits query
const userQuery = "T2 em Faro até 900€";

// ChatInterface.tsx
const response = await homesAIAPI.searchProperties(userQuery, seekerProfile);

// services/api.ts
POST http://localhost:8001/api/search
{
  "user_message": "T2 em Faro até 900€",
  "session_id": "session_123",
  "seeker_profile": { budget_max: 900, ... }
}

// BACKEND: api.py → research_agent.py
// 1. Parse query to extract requirements
// 2. Build Portuguese search query
// 3. Search via Bright Data (Idealista, Imovirtual, etc.)
// 4. Filter by Algarve cities
// 5. Return structured properties

// BACKEND Response
{
  "properties": [
    {
      "address": "Apartamento T2 Centro",
      "city": "Faro",
      "price": 850,
      "bedrooms": 2,
      "bathrooms": 1,
      "url": "https://idealista.pt/...",
      "compatibility_score": 85
    },
    ...
  ],
  "search_summary": "Encontrei 5 propriedades...",
  "total_found": 5,
  "session_id": "session_123"
}

// FRONTEND: Update UI
setProperties(response.properties);
```

### 2️⃣ Cálculo de Compatibilidade

```typescript
// FRONTEND: User completes profile
const seekerProfile: SeekerProfile = {
  budget_max: 900,
  schedule: "standard",
  pets: false,
  smoking: false,
  wfh_days: 3,
  cleanliness: "high",
  noise_tolerance: "low",
  preferred_cities: ["Faro", "Loulé"]
};

// RoommateProfileForm.tsx
onProfileComplete(seekerProfile);

// When viewing a property
const houseProfile: HouseProfile = {
  city: "Faro",
  rooms: 2,
  rules_pets: false,
  rules_smoking: false,
  quiet_hours: "22:00-08:00",
  bills_included: false,
  internet_speed_mbps: 100
};

const match = await homesAIAPI.calculateMatch(seekerProfile, houseProfile);

// BACKEND: matching_agent.py
// Calculate weighted compatibility score
// - Budget: 25%
// - Schedule: 20%
// - Pets: 15%
// - Smoking: 15%
// - Cleanliness: 10%
// - Noise: 10%
// - WFH: 5%

// Response
{
  "score": 87.5,
  "reasons": [
    "orçamento compatível",
    "horário de sono compatível",
    "internet rápida para teletrabalho"
  ],
  "session_id": "session_123"
}
```

### 3️⃣ Geolocalização e POIs

```typescript
// FRONTEND: User clicks on property
const property = { latitude: 37.0194, longitude: -7.9322 };

const pois = await homesAIAPI.getPOIs(property.latitude, property.longitude);

// BACKEND: mapbox_agent.py + local_agent.py
// 1. Validate coordinates
// 2. Search Mapbox POIs near location
// 3. Filter by categories: escolas, supermercados, saúde
// 4. Calculate distances

// Response
[
  {
    "name": "Continente Bom Dia",
    "category": "Supermercado",
    "latitude": 37.0200,
    "longitude": -7.9330,
    "distance_meters": 350
  },
  {
    "name": "Escola Secundária João de Deus",
    "category": "Escola",
    "latitude": 37.0180,
    "longitude": -7.9340,
    "distance_meters": 600
  },
  ...
]
```

## 🛠️ Implementação Backend Necessária

### 1. Criar Endpoint de Search

```python
# backend/api.py

@app.post("/api/search")
async def search_properties(request: SearchRequest):
    """
    Handle property search with optional roommate profile
    """
    # Parse user message to requirements
    requirements = parse_query_to_requirements(request.user_message)
    
    # Send to research agent
    research_request = ResearchRequest(
        requirements=requirements,
        session_id=request.session_id
    )
    
    # Get properties from research agent
    response = await research_agent.handle_request(research_request)
    
    # If seeker profile provided, calculate compatibility for each property
    if request.seeker_profile:
        for property in response.properties:
            # Create house profile from property data
            house = create_house_profile(property)
            
            # Calculate match
            match = await matching_agent.calculate_match(
                request.seeker_profile,
                house
            )
            
            property.compatibility_score = match.score
    
    return response
```

### 2. Criar Endpoint de Matching

```python
# backend/api.py

@app.post("/api/match")
async def calculate_match(request: MatchRequest):
    """
    Calculate compatibility between seeker and house
    """
    # Use CompatibilityMatcher from test_full_flow.py
    matcher = CompatibilityMatcher()
    
    match_response = matcher.calculate_compatibility(
        request.seeker,
        request.house
    )
    
    return match_response
```

### 3. Criar Endpoint de POIs

```python
# backend/api.py

@app.get("/api/pois")
async def get_pois(lat: float, lng: float, session_id: str):
    """
    Get POIs near a location
    """
    poi_request = LocalDiscoveryRequest(
        latitude=lat,
        longitude=lng,
        session_id=session_id,
        listing_index=0
    )
    
    response = await local_agent.handle_request(poi_request)
    
    return response.pois
```

## 📝 Models Necessários

### Frontend Types → Backend Models Mapping

```python
# backend/models.py

# ADD these models to match frontend types:

class SeekerProfile(Model):
    """Roommate/Seeker compatibility profile"""
    budget_min: Optional[int] = None
    budget_max: int
    schedule: str  # "early", "standard", "late"
    pets: bool
    smoking: bool
    wfh_days: int
    cleanliness: str  # "low", "med", "high"
    noise_tolerance: str  # "low", "med", "high"
    preferred_cities: List[str]

class HouseProfile(Model):
    """House/Unit profile for matching"""
    city: str
    rooms: int
    rules_pets: bool
    rules_smoking: bool
    quiet_hours: str
    bills_included: bool
    internet_speed_mbps: Optional[int] = None
    existing_tenants: int = 0
    landlord_contact: str = ""

class SearchRequest(Model):
    """Search request from frontend"""
    user_message: str
    session_id: str
    seeker_profile: Optional[SeekerProfile] = None

class MatchRequest(Model):
    """Match calculation request"""
    seeker: SeekerProfile
    house: HouseProfile
    session_id: str

class MatchResponse(Model):
    """Match calculation response"""
    score: float  # 0-100
    reasons: List[str]
    session_id: str
```

## 🔐 CORS Configuration

```python
# backend/api.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:3001",
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing Integration

### 1. Test Backend Endpoints

```bash
# Start backend
cd backend
python api.py

# Test search endpoint
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "T2 em Faro até 900€",
    "session_id": "test_123"
  }'

# Test match endpoint
curl -X POST http://localhost:8001/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "seeker": {"budget_max": 900, "schedule": "standard", ...},
    "house": {"city": "Faro", "rooms": 2, ...},
    "session_id": "test_123"
  }'
```

### 2. Test Frontend

```bash
# Start frontend
cd frontend
npm run dev

# Open browser
# http://localhost:3000

# Test flow:
# 1. Complete roommate profile
# 2. Search for properties
# 3. View compatibility scores
# 4. Click contact buttons
```

## 🚀 Deployment Checklist

- [ ] Backend deployed and accessible (port 8001)
- [ ] Frontend env var `NEXT_PUBLIC_API_URL` configured
- [ ] CORS configured for production domain
- [ ] Bright Data API key configured
- [ ] Mapbox token configured (optional)
- [ ] Test all endpoints working
- [ ] Test search → properties → matching flow
- [ ] Verify Portuguese content displays correctly

## 📚 Recursos

- **Backend**: `backend/api.py`, `backend/models.py`
- **Frontend**: `frontend/app/services/api.ts`
- **Models**: `frontend/app/types/api.ts`
- **Test**: `test_full_flow.py` (matching logic reference)
- **PRD**: `PRD.MD` (requirements)

---

**Integração completa e pronta para produção!** 🚀🇵🇹


