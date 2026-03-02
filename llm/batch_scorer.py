import json
from pathlib import Path
from scoring_engine import score_conversation   # FIXED IMPORT


# ── Resolve correct root path ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "transcription" / "sample_outputs"
OUTPUT_DIR = BASE_DIR / "analysis_results"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Files to skip ─────────────────────────────────────────
SKIP_FILES = {
    "chat_004.json",
    "chat_005.json",
    "chat_006.json",
    "call_transcript_3.txt",
    "call_transcript_4.txt",
    "call_transcript_6.txt",
}

MIN_CHARS = 100


def extract_text(file: Path):
    try:
        if file.suffix == ".txt":
            text = file.read_text(encoding="utf-8", errors="ignore").strip()
        elif file.suffix == ".json":
            data = json.loads(file.read_text(encoding="utf-8", errors="ignore"))
            text = data.get("conversation") or data.get("transcript") or ""
            text = text.strip()
        else:
            return None

        return text if len(text) >= MIN_CHARS else None

    except Exception as e:
        print(f"  ❌ Read error: {e}")
        return None


def run_batch():
    if not INPUT_DIR.exists():
        print(f"\n❌ Folder not found: {INPUT_DIR}")
        return

    all_files = sorted(
        f for f in INPUT_DIR.glob("*")
        if f.suffix in {".txt", ".json"}
        and f.name not in SKIP_FILES
    )

    if not all_files:
        print(f"\n❌ No valid files in {INPUT_DIR}")
        return

    print(f"\n📂 Batch Scorer")
    print(f"   Input  : {INPUT_DIR}")
    print(f"   Output : {OUTPUT_DIR}")
    print(f"   Files  : {len(all_files)} to score\n")
    print("─" * 60)

    for i, file in enumerate(all_files, 1):
        print(f"\n[{i}/{len(all_files)}] {file.name}")

        content = extract_text(file)
        if content is None:
            print("  ⚠️ Skipped — too short")
            continue

        try:
            result = score_conversation(content)
        except Exception as e:
            print(f"  ❌ Scoring error: {e}")
            continue

        out_path = OUTPUT_DIR / f"scored_{file.stem}.json"

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  ✅ Saved: {out_path.name}")


if __name__ == "__main__":
    run_batch()