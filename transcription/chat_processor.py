import os
import json
from pathlib import Path

# ==============================
# PATHS
# ==============================
BASE_DIR      = Path(__file__).resolve().parent.parent
CHAT_FOLDER   = BASE_DIR / "sample_data" / "chats"
OUTPUT_FOLDER = BASE_DIR / "transcription" / "sample_outputs"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ==============================
# SINGLE FILE (called by app.py)
# ==============================
def process_chat_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return {"conversation": text}


# ==============================
# FOLDER BATCH (run directly)
# ==============================
def process_chat_folder(folder_path=None):
    folder    = Path(folder_path) if folder_path else CHAT_FOLDER
    txt_files = sorted([f for f in folder.iterdir() if f.suffix == ".txt"]) if folder.exists() else []

    if not folder.exists():
        print(f"❌ Chat folder not found: {folder}")
        print(f"   Create: sample_data/chats/ and add .txt files")
        return []

    if not txt_files:
        print(f"❌ No .txt files found in: {folder}")
        print(f"   Add chat .txt files to sample_data/chats/")
        return []

    print(f"\n💬 Found {len(txt_files)} chat files in {folder.name}/\n" + "─"*50)

    results = []
    for count, file in enumerate(txt_files, 1):
        print(f"\n[{count}/{len(txt_files)}] {file.name}")
        try:
            text = file.read_text(encoding="utf-8").strip()
            if not text:
                print(f"  ⚠️  Skipped — empty file")
                continue

            data = {"chat_id": f"chat_{count:03}", "file_name": file.name, "conversation": text}

            out_file = OUTPUT_FOLDER / f"chat_{count:03}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            preview = text.splitlines()[0][:80] if text.splitlines() else ""
            print(f"  📄 Length  : {len(text)} chars")
            print(f"  📝 Preview : {preview}...")
            print(f"  💾 Saved   : {out_file.name}")
            results.append(data)

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n{'─'*50}")
    print(f"✅ Done — {len(results)} chat files saved to {OUTPUT_FOLDER.name}/\n")
    return results



if __name__ == "__main__":
    process_chat_folder()