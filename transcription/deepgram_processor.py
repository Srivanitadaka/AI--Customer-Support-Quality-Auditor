import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")

API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not API_KEY:
    print("WARNING: DEEPGRAM_API_KEY not found in config/.env")
else:
    print("Deepgram API Loaded")

AUDIO_FOLDER  = BASE_DIR / "sample_data" / "audio"
OUTPUT_FOLDER = BASE_DIR / "transcription" / "sample_outputs"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

DEEPGRAM_URL = (
    "https://api.deepgram.com/v1/listen"
    "?model=nova-2&punctuate=true&diarize=true&utterances=true"
)


def _format_utterances(utterances: list) -> str:
    speaker_map = {}
    lines = []
    for u in utterances:
        spk = u.get("speaker", 0)
        if spk not in speaker_map:
            speaker_map[spk] = "Agent" if len(speaker_map) == 0 else "Customer"
        text = u.get("transcript", "").strip()
        if text:
            lines.append(f"{speaker_map[spk]}: {text}")
    return "\n".join(lines)


def transcribe_audio(file_path: str, retries: int = 3) -> str:
    if not API_KEY:
        return "Transcription unavailable - DEEPGRAM_API_KEY not set"
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"  File: {os.path.basename(file_path)} ({round(size_mb, 2)} MB)")

    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "audio/mpeg" if str(file_path).endswith(".mp3") else "application/octet-stream"
    }

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(f"  [Deepgram] Attempt {attempt}/{retries}...")
            with open(file_path, "rb") as audio:
                response = requests.post(
                    DEEPGRAM_URL, headers=headers, data=audio, timeout=180
                )

            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"  [Deepgram] Error: {last_error}")
                time.sleep(2 ** attempt)
                continue

            result     = response.json()
            utterances = result.get("results", {}).get("utterances")

            if utterances:
                transcript = _format_utterances(utterances)
            else:
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]

            print(f"  [Deepgram] Success ({len(transcript)} chars)")
            return transcript

        except requests.exceptions.ConnectTimeout:
            last_error = "Connection timed out"
            print(f"  [Deepgram] Timeout on attempt {attempt} - retrying in {3*attempt}s...")
            time.sleep(3 * attempt)

        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)[:80]}"
            print(f"  [Deepgram] Connection error attempt {attempt} - retrying...")
            time.sleep(3 * attempt)

        except Exception as e:
            last_error = str(e)
            print(f"  [Deepgram] Exception: {last_error}")
            time.sleep(2)

    return f"Transcription failed after {retries} attempts: {last_error}"


def process_call_transcript(file_path: str) -> str:
    """Called by app.py for single uploaded audio file."""
    text = transcribe_audio(file_path)
    return text if text and text.strip() else "No transcript available"


def process_audio_folder(folder_path=None):
    """Batch transcribe all audio in folder. Run directly."""
    folder    = Path(folder_path) if folder_path else AUDIO_FOLDER
    supported = (".m4a", ".mp3", ".wav")
    files     = [f for f in folder.iterdir() if f.suffix.lower() in supported]

    if not files:
        print(f"No audio files found in {folder}")
        return []

    print(f"\nFound {len(files)} audio files in {folder.name}/\n" + "-"*50)
    results = []

    for count, file in enumerate(sorted(files), 1):
        print(f"\n[{count}/{len(files)}] {file.name}")
        transcript = transcribe_audio(str(file))
        out_file   = OUTPUT_FOLDER / f"call_transcript_{count}.txt"
        out_file.write_text(transcript, encoding="utf-8")
        print(f"  Saved -> {out_file.name}")
        results.append({"file": file.name, "transcript": transcript})

    print(f"\nDone - {len(results)} transcripts saved to {OUTPUT_FOLDER.name}/\n")
    return results


if __name__ == "__main__":
    process_audio_folder()