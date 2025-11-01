# 🚀 Quick Setup Instructions

## Current Status

✅ `.env` file created at: `backend\.env`  
❌ API keys need to be added

## 📝 Steps to Complete Setup:

### 1. Open the .env file
Navigate to:
```
C:\Users\jstme\Desktop\Pedro\AI Hackathon\Algarve_Hack\backend\.env
```

Open with Notepad, VS Code, or any text editor.

### 2. Add Your API Keys

Find these lines and replace the placeholder values:

```env
ASI_API_KEY=your_asi_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MAPBOX_API_KEY=your_mapbox_api_key_here
```

### 3. Get API Keys (Free Tiers Available)

#### ASI:1 API (REQUIRED)
- **URL**: https://asi1.ai/
- **Purpose**: Powers the AI that understands user queries
- **Free Tier**: Check their website
- **Key format**: Usually starts with `sk-`

#### Tavily API (REQUIRED for search)
- **URL**: https://tavily.com/
- **Purpose**: Searches for property listings
- **Free Tier**: Available
- **Key format**: Usually starts with `tvly-`

#### Mapbox API (REQUIRED for maps)
- **URL**: https://mapbox.com/
- **Purpose**: Shows properties on map
- **Free Tier**: Generous free tier (50k requests/month)
- **Key format**: Starts with `pk.`

### 4. Restart Backend

After adding keys, restart the backend:

```powershell
# Stop the current backend (Ctrl+C in the terminal)
# Then run:
cd "C:\Users\jstme\Desktop\Pedro\AI Hackathon\Algarve_Hack\backend"
py -3.12 main.py
```

### 5. Test It

Once restarted, try asking the chatbot:
- "Procuro apartamento de 2 quartos em Lisboa até 300k"
- "I need a 2 bedroom apartment in Lisbon under 300k"

It should now:
1. ✅ Understand your query
2. ✅ Extract requirements (bedrooms, budget, location)
3. ✅ Search for properties
4. ✅ Display results

## 🐛 Troubleshooting

**If you still see "How can I help you find a home?" without results:**
- Check that API keys are correct in `.env`
- Make sure there are no quotes around the keys
- Restart the backend after editing `.env`

**If you see "CONFIGURATION ERROR":**
- The ASI_API_KEY is missing or invalid
- Double-check the key in `.env`

**Backend logs showing errors:**
- Check backend terminal for specific error messages
- Ensure Python 3.12 is being used (not 3.14)

## ✅ Success Criteria

When properly configured, you should see in backend logs:
```
🔗 scoping_agent: Querying ASI:1 API
✅ Requirements gathered for session...
```

And the chatbot should return actual property search results!

---

**Need more help?** See `SETUP_REQUIRED.md` for detailed information.

