import json
from pathlib import Path

ANALYSIS_DIR = Path("../analysis_results")

files = list(ANALYSIS_DIR.glob("*.json"))

print(f"\nFound {len(files)} analysis files\n")

for file in files:

    print(f"Checking: {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Required fields
    checks = [
        "summary" in data,
        "sentiment" in data,
        "performance" in data,
        "issue" in data,
        "resolution" in data,
    ]

    # Empty value check
    value_checks = [
        bool(data.get("summary")),
        bool(data.get("sentiment")),
        bool(data.get("performance")),
        bool(data.get("issue")),
        bool(data.get("resolution")),
    ]

    if all(checks) and all(value_checks):
        print("✅ Structure looks valid\n")
    else:
        print("❌ Missing required fields or empty values\n")
