# ⚠️ CRITICAL: API KEYS REQUIRED

## 🚨 Current Status

The backend is running but **cannot process queries** because the required API keys are not configured.

## 📋 What You Need

The Estate Search System requires API keys from multiple services to function:

### 1. **ASI:1 API** (CRITICAL - Required for ALL agents)
- **Purpose**: Powers the LLM for all intelligent agents (scoping, research, analysis)
- **Sign up**: https://asi1.ai/
- **Why it's needed**: Every agent uses this to understand queries and generate responses

### 2. **BrightData API** 
- **Purpose**: Web scraping for property listings
- **Sign up**: https://brightdata.com/
- **Why it's needed**: Scrapes real estate websites for property data

### 3. **Firecrawl API**
- **Purpose**: Advanced web crawling
- **Sign up**: https://firecrawl.dev/
- **Why it's needed**: Extracts structured data from property websites

### 4. **Tavily API**
- **Purpose**: Search engine for community information
- **Sign up**: https://tavily.com/
- **Why it's needed**: Finds community data, school info, safety ratings

### 5. **Vapi API**
- **Purpose**: Voice AI for phone calls
- **Sign up**: https://vapi.ai/
- **Why it's needed**: Handles negotiation phone calls with property owners

### 6. **Mapbox API**
- **Purpose**: Geocoding and maps
- **Sign up**: https://mapbox.com/
- **Why it's needed**: Converts addresses to coordinates, displays maps

## 🔧 Setup Steps

### Step 1: Create .env file

```powershell
cd backend
Copy-Item env_template.txt .env
```

### Step 2: Get API Keys

Visit each service website and sign up for API access:

1. **ASI:1** (Start here - this is the most critical)
   - Go to https://asi1.ai/
   - Sign up for an account
   - Get your API key
   - Model to use: `asi1-mini`

2. **BrightData**
   - Go to https://brightdata.com/
   - Sign up for scraping API
   - Get your API key

3. **Firecrawl**
   - Go to https://firecrawl.dev/
   - Sign up
   - Get your API key

4. **Tavily**
   - Go to https://tavily.com/
   - Sign up
   - Get your API key

5. **Vapi**
   - Go to https://vapi.ai/
   - Sign up
   - Get your API key and assistant ID

6. **Mapbox**
   - Go to https://mapbox.com/
   - Sign up
   - Get your API key

### Step 3: Configure .env file

Open `backend/.env` and replace the placeholder values:

```env
ASI_API_KEY=sk-your-actual-asi-key-here
BRIGHT_DATA_API_KEY=your-actual-brightdata-key-here
FIRECRAWL_API_KEY=your-actual-firecrawl-key-here
TAVILY_API_KEY=tvly-your-actual-tavily-key-here
VAPI_API_KEY=your-actual-vapi-key-here
VAPI_ASSISTANT_ID=your-actual-assistant-id-here
MAPBOX_API_KEY=pk.your-actual-mapbox-key-here
```

### Step 4: Restart Backend

```powershell
# Stop current backend (if running)
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# Start backend with new configuration
cd backend
py -3.12 main.py
```

### Step 5: Verify Setup

Test that the API is working:

```powershell
$body = @{message = "Find me a 2 bedroom apartment in Lisbon under 300k"; session_id = "test123"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8080/api/chat" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

If successful, you should see actual property search results instead of "How can I help you find a home?"

## 🐛 Current Issue Explanation

**Why the test is failing:**

1. The backend starts successfully ✅
2. The API endpoints are accessible ✅
3. BUT: When a query is sent, the scoping agent's LLM fails because `ASI_API_KEY` is not set ❌
4. This causes the agent to return a default response instead of processing the query ❌
5. No properties are found because the query is never actually processed ❌

**The fix:**

Once you add the API keys (especially `ASI_API_KEY`), the system will:
1. Process user queries correctly
2. Extract requirements (bedrooms, budget, location)
3. Search for properties
4. Return real results
5. Pass the test successfully

## 💰 Cost Considerations

Most of these services offer free tiers:
- ASI:1: Check their pricing page
- Tavily: Free tier available
- Mapbox: Generous free tier
- BrightData: Free trial available
- Firecrawl: Free tier available
- Vapi: Pay-as-you-go

**For testing purposes**, you only need:
1. **ASI_API_KEY** (critical - all agents need this)
2. **TAVILY_API_KEY** (for search functionality)
3. **MAPBOX_API_KEY** (for maps)

The other keys can be added later if needed.

## 📞 Next Steps

1. Get at least the **ASI_API_KEY** to unblock development
2. Create the `.env` file with your keys
3. Restart the backend
4. Run the test again: `py -3.12 tests/test_search_flow.py`

## ✅ Success Criteria

When properly configured, the test output should show:
- ✅ Backend is running
- ✅ Requirements extracted (Location, Budget, Bedrooms)
- ✅ Total Found > 0
- ✅ Properties organized
- ✅ All assertions passed

---

**Need help?** Check the `env_template.txt` file in the backend directory for the complete template.

