# 🔑 API Key Authentication Issue - Troubleshooting

## Current Error
```
❌ scoping_agent: API Error 401: {"message":"failed to authenticate user"}
```

This means the ASI_API_KEY is being read from `.env` but is **not valid**.

## ✅ Quick Fixes

### 1. Check .env File Format

Open `backend\.env` and make sure your API key line looks EXACTLY like this:

```env
ASI_API_KEY=sk-your-actual-key-here
```

**Common Mistakes to Avoid:**
- ❌ `ASI_API_KEY="sk-your-key"` (no quotes!)
- ❌ `ASI_API_KEY= sk-your-key` (no space after =)
- ❌ `ASI_API_KEY=sk-your-key ` (no trailing space)
- ✅ `ASI_API_KEY=sk-your-actual-key` (correct!)

### 2. Verify Your API Key

1. Go to https://asi1.ai/
2. Log into your account
3. Navigate to API Keys section
4. Copy your key **exactly as shown**
5. Paste it into `.env` with NO quotes, NO spaces

### 3. Alternative LLM Options

If you don't have an ASI:1 API key yet, I can help you switch to using **OpenAI** or **Anthropic** instead:

#### Option A: Use OpenAI (ChatGPT)
```env
# Comment out ASI:1
# ASI_API_KEY=...

# Add OpenAI instead (if you want me to implement this)
OPENAI_API_KEY=sk-your-openai-key
```

#### Option B: Use Anthropic (Claude)
```env
# Comment out ASI:1
# ASI_API_KEY=...

# Add Anthropic instead (if you want me to implement this)
ANTHROPIC_API_KEY=sk-ant-your-key
```

**Let me know if you want me to add support for OpenAI or Anthropic!**

### 4. Test API Key Manually

You can test your ASI:1 API key with this PowerShell command:

```powershell
$headers = @{
    "Authorization" = "Bearer YOUR_API_KEY_HERE"
    "Content-Type" = "application/json"
}

$body = @{
    model = "asi1-mini"
    messages = @(
        @{
            role = "user"
            content = "Hello"
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri "https://api.asi1.ai/v1/chat/completions" -Method POST -Headers $headers -Body $body -UseBasicParsing
```

Replace `YOUR_API_KEY_HERE` with your actual key. If this returns 401, the key is invalid.

## 🔄 After Fixing

1. **Save** the `.env` file
2. **Restart** the backend (Ctrl+C and run `py -3.12 main.py` again)
3. **Test** by sending a message to the chatbot

## 📞 Need Help?

**Option 1**: Get a valid ASI:1 API key from https://asi1.ai/

**Option 2**: Let me know if you'd prefer to use:
- OpenAI (most popular, easy to get)
- Anthropic Claude (what I'm built on!)
- Another LLM service

I can modify the code to support any of these instead of ASI:1.

---

**Current Status**: System is working, just needs a valid API key! 🎯

