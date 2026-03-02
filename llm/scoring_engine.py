import os
import re
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / "config" / ".env")

API_KEY    = os.getenv("GROQ_API_KEY")
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
MODEL      = "llama-3.3-70b-versatile"

# ── Local compliance pre-scan ──────────────────────────────────────────
VIOLATION_KEYWORDS = {
    "rude_language":         ["shut up", "stupid", "idiot", "not my problem", "i don't care", "figure it out"],
    "gdpr_risk":             ["send me your password", "give me your card number", "your cvv", "social security", "your pin"],
    "false_promise":         ["i guarantee", "100% sure", "i promise you", "definitely will", "absolutely guaranteed"],
    "unprofessional_language": [" idk ", "whatever", " lol ", " lmao ", "bruh", "tbh", " omg "],
    "escalation_ignored":    ["i want to speak to a manager", "get me a supervisor", "i want to escalate"],
    "negative_language":     ["there's nothing i can do", "not our fault", "not my problem"],
}

def local_flag_check(text: str) -> list:
    text_lower = text.lower()
    flags = []
    for category, keywords in VIOLATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                flags.append({
                    "type":     category,
                    "trigger":  kw.strip(),
                    "severity": "high" if category in ("gdpr_risk", "rude_language") else "medium"
                })
                break
    return flags

# ── System prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Senior Customer Support Quality Analyst and Call Center Auditor with 15+ years of experience.
You evaluate support conversations with precision and fairness.
You ALWAYS return ONLY valid JSON — no markdown, no backticks, no text outside the JSON object."""

# ── Scoring prompt ─────────────────────────────────────────────────────
USER_PROMPT = """Analyze this customer support conversation thoroughly and return ONLY a valid JSON object.

Return EXACTLY this structure (all fields required):

{{
  "overall_score": <integer 0-100>,
  "grade": "<A|B|C|D|F>",
  "call_outcome": "<Resolved|Partially Resolved|Unresolved|Escalated>",
  "summary": "<2 sentence summary of the interaction quality>",

  "satisfaction": {{
    "rating": <float 1.0-5.0>,
    "sentiment": "<Positive|Neutral|Negative|Mixed>",
    "sentiment_score": <float 0.0-1.0>,
    "emotional_stability": "<Excellent|Good|Fair|Poor>",
    "customer_frustration": "<None|Low|Medium|High|Very High>",
    "frustration_reason": "<brief reason or 'None'>"
  }},

  "agent_quality": {{
    "language_clarity": <integer 0-20>,
    "professionalism":  <integer 0-20>,
    "time_efficiency":  <integer 0-20>,
    "response_efficiency": <integer 0-20>,
    "empathy_score":    <float 0.0-10.0>,
    "bias_detected":    <boolean>,
    "bias_notes":       "<description or 'None'>",
    "empathy_phrases_used": ["<phrase1>", "<phrase2>"],
    "calmed_customer":  <boolean>
  }},

  "dimension_scores": {{
    "empathy":                  <integer 0-10>,
    "professionalism":          <integer 0-10>,
    "compliance":               <integer 0-10>,
    "resolution_effectiveness": <integer 0-10>,
    "communication_clarity":    <integer 0-10>
  }},

  "model_metrics": {{
    "precision":   <float 0.0-1.0>,
    "recall":      <float 0.0-1.0>,
    "f1_score":    <float 0.0-1.0>,
    "confidence":  <float 0.0-1.0>,
    "notes": "<brief explanation of these confidence scores>"
  }},

  "violations": [
    {{
      "type":        "<category>",
      "quote":       "<near-exact quote from conversation>",
      "severity":    "<high|medium|low>",
      "explanation": "<why this is a violation>"
    }}
  ],

  "improvements": [
    {{
      "area":       "<area>",
      "suggestion": "<specific actionable change>",
      "example":    "<rewritten example of what agent should have said>"
    }}
  ],

  "highlights": ["<specific positive thing agent did>"],

  "issue_detected": "<main customer problem in one sentence>",
  "was_resolved":   <boolean>
}}

Scoring rules:
- overall_score = weighted: empathy*20 + professionalism*20 + compliance*20 + resolution*25 + clarity*15, divided by 10
- grade: A=90+, B=75+, C=60+, D=50+, F=below 50
- satisfaction.rating: derived from sentiment, resolution, and customer tone (1.0=terrible, 5.0=excellent)
- sentiment_score: 0.0=very negative, 1.0=very positive
- model_metrics: your confidence in detection accuracy (precision/recall/f1 of your own analysis)
- If violations list is empty return []
- If highlights list is empty return []

Conversation:
---
{conversation}
---"""


# ── Main scoring function ──────────────────────────────────────────────
def score_conversation(text: str) -> dict:
    if not text or len(text.strip()) < 20:
        return _empty_result("Conversation too short to analyze")
    if not API_KEY:
        return _empty_result("GROQ_API_KEY not set in config/.env")

    local_flags = local_flag_check(text)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":       MODEL,
        "temperature": 0.1,
        "max_tokens":  2000,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": USER_PROMPT.format(conversation=text[:6000])}
        ]
    }

    raw_output = None
    last_error  = None
    for attempt in range(3):
        try:
            print(f"  [Groq] Attempt {attempt+1}...")
            resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                raw_output = resp.json()["choices"][0]["message"]["content"]
                print(f"  [Groq] Success on attempt {attempt+1}")
                break
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:150]}"
                print(f"  [Groq] Error: {last_error}")
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = str(e)
            print(f"  [Groq] Exception: {last_error}")
            time.sleep(2)

    if not raw_output:
        return _empty_result(f"Groq API failed: {last_error}")

    try:
        clean = raw_output.strip().replace("```json","").replace("```","").strip()
        start = clean.find("{")
        end   = clean.rfind("}") + 1
        parsed = json.loads(clean[start:end])
    except Exception as e:
        print(f"  [Parse Error] {e}\n  Raw: {raw_output[:300]}")
        return _empty_result(f"Could not parse LLM response")

    # Merge local flags into violations
    llm_violations = parsed.get("violations", [])
    llm_types      = {v.get("type","").lower() for v in llm_violations}
    for flag in local_flags:
        if flag["type"].lower() not in llm_types:
            llm_violations.append({
                "type":        flag["type"],
                "quote":       f'Keyword detected: "{flag["trigger"]}"',
                "severity":    flag["severity"],
                "explanation": f"Auto-flagged: '{flag['trigger']}'"
            })
    parsed["violations"] = llm_violations

    return _normalize(parsed)


def _normalize(p: dict) -> dict:
    dims = p.get("dimension_scores", {})
    sat  = p.get("satisfaction", {})
    aq   = p.get("agent_quality", {})
    mm   = p.get("model_metrics", {})

    return {
        "overall_score":  int(p.get("overall_score", 0)),
        "grade":          str(p.get("grade", "F")),
        "call_outcome":   str(p.get("call_outcome", "Unresolved")),
        "summary":        str(p.get("summary", "")),
        "was_resolved":   bool(p.get("was_resolved", False)),
        "issue_detected": str(p.get("issue_detected", "Not identified")),

        "satisfaction": {
            "rating":             float(sat.get("rating", 0)),
            "sentiment":          str(sat.get("sentiment", "Neutral")),
            "sentiment_score":    float(sat.get("sentiment_score", 0.5)),
            "emotional_stability":str(sat.get("emotional_stability", "Fair")),
            "customer_frustration": str(sat.get("customer_frustration", "Low")),
            "frustration_reason": str(sat.get("frustration_reason", "None")),
        },

        "agent_quality": {
            "language_clarity":     int(aq.get("language_clarity", 0)),
            "professionalism":      int(aq.get("professionalism", 0)),
            "time_efficiency":      int(aq.get("time_efficiency", 0)),
            "response_efficiency":  int(aq.get("response_efficiency", 0)),
            "empathy_score":        float(aq.get("empathy_score", 0)),
            "bias_detected":        bool(aq.get("bias_detected", False)),
            "bias_notes":           str(aq.get("bias_notes", "None")),
            "empathy_phrases_used": list(aq.get("empathy_phrases_used", [])),
            "calmed_customer":      bool(aq.get("calmed_customer", False)),
        },

        "dimension_scores": {
            "empathy":                  int(dims.get("empathy", 0)),
            "professionalism":          int(dims.get("professionalism", 0)),
            "compliance":               int(dims.get("compliance", 0)),
            "resolution_effectiveness": int(dims.get("resolution_effectiveness", 0)),
            "communication_clarity":    int(dims.get("communication_clarity", 0)),
        },

        "model_metrics": {
            "precision":  float(mm.get("precision", 0)),
            "recall":     float(mm.get("recall", 0)),
            "f1_score":   float(mm.get("f1_score", 0)),
            "confidence": float(mm.get("confidence", 0)),
            "notes":      str(mm.get("notes", "")),
        },

        # Legacy fields for backward compat
        "scores":       dims,
        "sentiment":    sat.get("sentiment", "Neutral").lower(),

        "violations":   p.get("violations", []),
        "improvements": p.get("improvements", []),
        "highlights":   p.get("highlights", []),
    }


def _empty_result(reason: str) -> dict:
    empty_scores = {"empathy":0,"professionalism":0,"compliance":0,"resolution_effectiveness":0,"communication_clarity":0}
    return {
        "overall_score": 0, "grade": "F", "call_outcome": "Unresolved",
        "summary": reason, "was_resolved": False, "issue_detected": "Unknown",
        "satisfaction":  {"rating":0,"sentiment":"Unknown","sentiment_score":0,"emotional_stability":"Unknown","customer_frustration":"Unknown","frustration_reason":"N/A"},
        "agent_quality": {"language_clarity":0,"professionalism":0,"time_efficiency":0,"response_efficiency":0,"empathy_score":0,"bias_detected":False,"bias_notes":"N/A","empathy_phrases_used":[],"calmed_customer":False},
        "dimension_scores": empty_scores,
        "model_metrics": {"precision":0,"recall":0,"f1_score":0,"confidence":0,"notes":"Analysis failed"},
        "scores": empty_scores, "sentiment": "unknown",
        "violations":[], "improvements":[], "highlights":[]
    }


if __name__ == "__main__":
    test = """
Agent: Thank you for calling support, this is James. How can I help?
Customer: Hi, I've been charged twice this month and I'm very upset!
Agent: I'm really sorry to hear that. I completely understand how frustrating that must be. Let me pull up your account right away.
Agent: I can see the duplicate charge. I'm processing a full refund now and it will appear in 2-3 business days.
Customer: Thank you so much, that's a relief.
Agent: Of course! Is there anything else I can help you with today?
"""
    import json
    result = score_conversation(test)
    print(json.dumps(result, indent=2))