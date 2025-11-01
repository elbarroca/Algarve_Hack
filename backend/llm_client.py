"""
LLM Client for Estate uAgents System
====================================

This file contains the shared LLM client that all uAgents use to communicate with ASI:1.
"""

import aiohttp
import json
import re
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ASI:1 API configuration from environment variables
ASI_API_KEY = os.getenv("ASI_API_KEY")
ASI_API_URL = os.getenv("ASI_API_URL", "https://api.asi1.ai/v1/chat/completions")
ASI_MODEL = os.getenv("ASI_MODEL", "asi1-mini")


class SimpleLLMAgent:
    """Base class for LLM-powered agents using ASI:1"""

    def __init__(self, name: str, system_prompt: Optional[str] = None):
        self.name = name
        self.api_key = ASI_API_KEY
        self.api_url = ASI_API_URL
        self.model = ASI_MODEL
        self.system_prompt = system_prompt or "You are a specialized AI agent. Provide clear, structured responses."

    async def query_llm(self, prompt: str, temperature: float = 0.1, max_tokens: int = 300) -> dict:
        """Query ASI:1 API with a prompt and get response"""

        if not self.api_key:
            return {
                "success": False,
                "content": "ASI_API_KEY not configured in environment variables"
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            "max_tokens": max_tokens,
        }

        try:
            print(f"🔗 {self.name}: Querying ASI:1 API")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        return {
                            "success": True,
                            "content": content,
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ {self.name}: API Error {response.status}: {error_text}")
                        return {
                            "success": False,
                            "content": f"API Error {response.status}: {error_text}",
                        }
        except Exception as e:
            print(f"💥 {self.name}: Error querying ASI:1: {e}")
            return {"success": False, "content": f"Request Error: {str(e)}"}

    def parse_json_response(self, content: str) -> Dict:
        """Parse JSON response from LLM, handling markdown formatting and malformed JSON"""
        try:
            # Remove markdown code blocks if present
            content = re.sub(
                r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE
            )
            content = content.strip()
            
            # Try to parse as-is first
            return json.loads(content)
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ {self.name}: JSON parsing error: {e}")
            print(f"🔍 Trying to fix malformed JSON...")
            
            try:
                # Try to fix common JSON issues
                fixed_content = content
                
                # Fix unterminated strings - find the last complete JSON object
                # This is a simple heuristic for handling malformed responses
                brace_count = 0
                quote_count = 0
                in_string = False
                escape_next = False
                last_complete_pos = 0
                
                for i, char in enumerate(fixed_content):
                    if escape_next:
                        escape_next = False
                        continue
                        
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        quote_count += 1
                        continue
                        
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                last_complete_pos = i + 1
                
                # If we found a complete JSON object, try parsing it
                if last_complete_pos > 0:
                    complete_json = fixed_content[:last_complete_pos]
                    print(f"🔧 Trying to parse complete JSON up to position {last_complete_pos}")
                    return json.loads(complete_json)
                
                # Try removing trailing incomplete content
                lines = fixed_content.split('\n')
                for i in range(len(lines), 0, -1):
                    try:
                        test_content = '\n'.join(lines[:i])
                        return json.loads(test_content)
                    except:
                        continue
                
                # If all else fails, try to extract any JSON-like structure
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                matches = re.findall(json_pattern, fixed_content)
                if matches:
                    for match in matches:
                        try:
                            return json.loads(match)
                        except:
                            continue
                
                print(f"💥 Could not fix malformed JSON. Content preview: {content[:200]}...")
                return {}
                
            except Exception as fix_error:
                print(f"💥 Failed to fix JSON: {fix_error}")
                print(f"🔍 Original error: {e}")
                return {}

    async def query_with_json(self, prompt: str, temperature: float = 0.1) -> Dict:
        """Query LLM and automatically parse JSON response"""
        result = await self.query_llm(prompt, temperature=temperature)

        if result["success"]:
            parsed = self.parse_json_response(result["content"])
            if parsed:
                return {"success": True, "data": parsed}
            else:
                return {"success": False, "data": {}, "error": "Failed to parse JSON"}
        else:
            return {"success": False, "data": {}, "error": result["content"]}