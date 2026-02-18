# genai/analyzer.py  ← SAVE THIS EXACTLY
import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load API key
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / "config" / ".env")

API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"🔑 API Key loaded: {API_KEY[:10]}..." if API_KEY else "❌ NO API KEY!")

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"

def analyze_text(text):
    print(f"📝 Analyzing text length: {len(text)} chars")
    
    # Safety check
    if not text or len(text.strip()) < 10:
        print("⚠️ Text too short")
        return {
            "summary": "Short conversation - insufficient data",
            "sentiment": "neutral", 
            "performance": "unknown",
            "issue": "none",
            "resolution": "none"
        }
    
    PROMPT = f"""Analyze this conversation. Return ONLY valid JSON:

{{
  "summary": "1 sentence summary",
  "sentiment": "positive|negative|neutral", 
  "performance": "excellent|good|average|poor",
  "issue": "main customer problem or 'none'",
  "resolution": "how it was resolved or 'none'"
}}

Conversation:
{text[:4000]}"""  # Truncate long text
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}]
    }
    
    if not API_KEY:
        print("❌ Missing OPENROUTER_API_KEY")
        return {
            "summary": "API Key missing - check .env file",
            "sentiment": "error",
            "performance": "error", 
            "issue": "configuration",
            "resolution": "add OPENROUTER_API_KEY"
        }
    
    try:
        print("🌐 Calling OpenRouter API...")
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        print(f"📡 API Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return {
                "summary": f"API Error {response.status_code}",
                "sentiment": "error",
                "performance": "error",
                "issue": response.text[:100],
                "resolution": "check API key/quota"
            }
        
        result = response.json()
        raw_output = result["choices"][0]["message"]["content"]
        print(f"🤖 Raw LLM: {raw_output[:100]}...")
        
        # Clean JSON
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        clean_json = raw_output[start:end]
        
        parsed = json.loads(clean_json)
        
        return {
            "summary": parsed.get("summary", "No summary"),
            
        }
        
    except Exception as e:
        print(f"💥 Exception: {str(e)}")
        return {
            "summary": f"Error: {str(e)[:50]}",
            
        }
