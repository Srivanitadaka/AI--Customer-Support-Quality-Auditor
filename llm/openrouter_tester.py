import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import json
import re

# ==============================
# LOAD ENV
# ==============================
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "config" / ".env"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found")

print("API Key Loaded")

# ==============================
# PATHS
# ==============================
TRANSCRIPT_DIR = BASE_DIR / "transcription" / "sample_outputs"
OUTPUT_DIR = BASE_DIR / "analysis_results"

OUTPUT_DIR.mkdir(exist_ok=True)

# ==============================
# API CONFIG
# ==============================
URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

MODEL = "mistralai/mistral-7b-instruct"

# ==============================
# PROMPT (TEST COMPATIBLE)
# ==============================
PROMPT = """
You are a Customer Support QA Analyst.

Analyze the conversation and return ONLY valid JSON.

Use EXACT field names below:

{{
  "summary": "",
  "sentiment": "",
  "performance": "",
  "issue": "",
  "resolution": ""
}}

Rules:
- No markdown
- No backticks
- No extra text
- Fill all fields

Conversation:
----------------
{data}
----------------
"""

# ==============================
# CLEAN LLM OUTPUT
# ==============================
def clean_llm_json(text):

    # Remove markdown fences
    text = re.sub(r"```json|```", "", text).strip()

    # Extract JSON block
    start = text.find("{")
    end = text.rfind("}") + 1
    text = text[start:end]

    return json.loads(text)

# ==============================
# NORMALIZE OUTPUT
# ==============================
def normalize_output(parsed):

    return {
        "summary": parsed.get("summary", ""),
        "sentiment": parsed.get("sentiment", ""),
        "performance": parsed.get("performance", ""),
        "issue": parsed.get("issue", ""),
        "resolution": parsed.get("resolution", "")
    }

# ==============================
# READ FILES
# ==============================
files = list(TRANSCRIPT_DIR.glob("*"))

if not files:
    raise FileNotFoundError("No transcript/chat files found")

print(f"Found {len(files)} files\n")

for i, file in enumerate(files, 1):

    print(f"Processing: {file.name}")

    # ---------- TXT ----------
    if file.suffix == ".txt":
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

    # ---------- JSON ----------
    elif file.suffix == ".json":
        with open(file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        content = json.dumps(json_data, indent=2)

    else:
        print("Skipped unsupported file\n")
        continue

    # -----------------------------
    # Trim long conversations
    # -----------------------------
    MAX_CHARS = 12000
    content = content[:MAX_CHARS]

    prompt_text = PROMPT.format(data=content)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }

    # ==============================
    # RETRY LOGIC
    # ==============================
    retries = 3
    result = None

    for attempt in range(retries):

        try:
            response = requests.post(
                URL,
                headers=HEADERS,
                json=payload,
                timeout=120
            )

            result = response.json()

            if "choices" in result:
                break
            else:
                print("API Error:", result)

        except Exception as e:
            print(f"Retry {attempt+1} failed:", e)

    # If still failed → skip
    if not result or "choices" not in result:
        print("Skipped due to repeated API failure\n")
        continue

    raw_output = result["choices"][0]["message"]["content"]

    # ==============================
    # CLEAN + PARSE JSON
    # ==============================
    try:
        parsed_output = clean_llm_json(raw_output)
    except:
        print("Failed to parse JSON\n")
        continue

    # Normalize schema
    safe_output = normalize_output(parsed_output)

    # ==============================
    # SAVE OUTPUT
    # ==============================
    output_file = OUTPUT_DIR / f"analysis_{i}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(safe_output, f, indent=4)

    print(f"Saved -> {output_file.name}\n")

print("Analysis completed")
print("Loaded Key Preview:", API_KEY[:10])
