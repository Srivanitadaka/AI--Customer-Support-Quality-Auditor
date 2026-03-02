import json
from pathlib import Path

BASE_DIR      = Path(__file__).resolve().parent.parent
ANALYSIS_DIR  = BASE_DIR / "analysis_results"

REQUIRED_FIELDS = ["summary", "sentiment", "overall_score", "grade",
                   "scores", "violations", "improvements", "highlights",
                   "issue_detected", "was_resolved"]

SCORE_FIELDS = ["empathy", "professionalism", "compliance",
                "resolution_effectiveness", "communication_clarity"]


def test_all():
    files = sorted(ANALYSIS_DIR.glob("scored_*.json"))

    if not files:
        print(f"\n⚠️  No scored files found in {ANALYSIS_DIR}")
        print("   Run: python batch_scorer.py first\n")
        return

    print(f"\n🧪 Testing {len(files)} scored files in {ANALYSIS_DIR.name}/\n")
    print("─" * 60)

    passed = 0
    failed = 0

    for file in files:
        print(f"\n📄 {file.name}")
        errors = []

        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ❌ Cannot read file: {e}")
            failed += 1
            continue

        # Check required top-level fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"Missing field: '{field}'")

        # Check scores sub-fields
        scores = data.get("scores", {})
        for sf in SCORE_FIELDS:
            if sf not in scores:
                errors.append(f"Missing score: 'scores.{sf}'")
            elif not isinstance(scores[sf], (int, float)):
                errors.append(f"Score not a number: 'scores.{sf}' = {scores[sf]}")
            elif not (0 <= scores[sf] <= 10):
                errors.append(f"Score out of range: 'scores.{sf}' = {scores[sf]}")

        # Check overall_score range
        overall = data.get("overall_score", -1)
        if not isinstance(overall, (int, float)) or not (0 <= overall <= 100):
            errors.append(f"overall_score out of range: {overall}")

        # Check grade valid
        if data.get("grade") not in {"A", "B", "C", "D", "F", "N/A"}:
            errors.append(f"Invalid grade: {data.get('grade')}")

        # Check non-empty summary
        if not data.get("summary", "").strip():
            errors.append("summary is empty")

        # Report
        if not errors:
            grade   = data.get("grade", "?")
            score   = data.get("overall_score", 0)
            vcount  = len(data.get("violations", []))
            hcount  = len(data.get("highlights", []))
            print(f"  ✅ PASS  |  Grade: {grade}  Score: {score}/100  Violations: {vcount}  Highlights: {hcount}")
            passed += 1
        else:
            print(f"  ❌ FAIL  |  {len(errors)} error(s):")
            for err in errors:
                print(f"     • {err}")
            failed += 1

    # ── Summary ──────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"🧪 Test Results: {passed} passed  |  {failed} failed  |  {len(files)} total\n")

    if failed == 0:
        print("🎉 All tests passed! Scoring engine output is valid.\n")
    else:
        print(f"⚠️  {failed} file(s) have issues. Check output above.\n")


if __name__ == "__main__":
    test_all()