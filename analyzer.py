import os
from dotenv import load_dotenv
from pathlib import Path
from llm.scoring_engine import score_conversation

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / "config" / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
print(f"🔑 Groq API Key loaded: {API_KEY[:10]}..." if API_KEY else "❌ GROQ_API_KEY missing!")


def analyze_text(text: str) -> dict:
    print(f"📝 Text length: {len(text)} chars")
    if not text or len(text.strip()) < 10:
        return _short_result()

    print("🧠 Running Quality Scoring Engine (Groq)...")
    scored = score_conversation(text)

    overall = scored.get("overall_score", 0)
    if   overall >= 90: performance = "excellent"
    elif overall >= 75: performance = "good"
    elif overall >= 60: performance = "average"
    else:               performance = "poor"

    violations   = scored.get("violations", [])
    improvements = scored.get("improvements", [])

    return {
        "summary":          scored.get("summary", ""),
        "sentiment":        scored.get("sentiment", "neutral"),
        "performance":      performance,
        "issue":            violations[0]["explanation"] if violations else "No violations",
        "resolution":       improvements[0]["suggestion"] if improvements else "No improvements needed",
        "overall_score":    scored.get("overall_score", 0),
        "grade":            scored.get("grade", "F"),
        "call_outcome":     scored.get("call_outcome", "Unresolved"),
        "was_resolved":     scored.get("was_resolved", False),
        "issue_detected":   scored.get("issue_detected", "Unknown"),
        "satisfaction":     scored.get("satisfaction", {}),
        "agent_quality":    scored.get("agent_quality", {}),
        "dimension_scores": scored.get("dimension_scores", {}),
        "scores":           scored.get("dimension_scores", {}),
        "model_metrics":    scored.get("model_metrics", {}),
        "violations":       scored.get("violations", []),
        "improvements":     scored.get("improvements", []),
        "highlights":       scored.get("highlights", []),
    }


def _short_result() -> dict:
    empty = {"empathy":0,"professionalism":0,"compliance":0,"resolution_effectiveness":0,"communication_clarity":0}
    return {
        "summary":"Conversation too short","sentiment":"neutral","performance":"unknown",
        "issue":"none","resolution":"none","overall_score":0,"grade":"N/A",
        "call_outcome":"Unresolved","was_resolved":False,"issue_detected":"none",
        "satisfaction":{},"agent_quality":{},"dimension_scores":empty,"scores":empty,
        "model_metrics":{},"violations":[],"improvements":[],"highlights":[]
    }