import os
import requests
from dotenv import load_dotenv
from pathlib import Path


# -------------------------
# Load API key
# -------------------------
#load_dotenv()
# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")

API_KEY = os.getenv("DEEPGRAM_API_KEY")

if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY not found")

print("✅ Deepgram API Loaded")

# -------------------------
# Paths
# -------------------------
AUDIO_FOLDER = "../sample_data/audio"
OUTPUT_FOLDER = "../transcription/sample_outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------------------------
# Endpoint
# -------------------------
url = "https://api.deepgram.com/v1/listen?model=nova-2"

headers = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/octet-stream"
}


# -------------------------
# Function
# -------------------------
def transcribe_audio(file_path):
    # ---- FILE SIZE DEBUG ----
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print("File size:", round(size_mb, 2), "MB")

    with open(file_path, "rb") as audio:
       response = requests.post(
    url,
    headers=headers,
    data=audio,
    timeout=600   # wait longer
)


    if response.status_code != 200:
        print(f"❌ Error → {file_path}")
        print(response.text)
        return "Audio transcription failed"

    result = response.json()

    transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]

    return transcript


# -------------------------
# Process files
# -------------------------
'''count = 1

for file in os.listdir(AUDIO_FOLDER):

    if file.endswith((".m4a", ".mp3", ".wav")):

        path = os.path.join(AUDIO_FOLDER, file)

        print(f"Processing → {file}")

        text = transcribe_audio(path)

        out_file = os.path.join(
            OUTPUT_FOLDER,
            f"call_transcript_{count}.txt"
        )

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)

        count += 1

print("\n✅ Audio transcripts saved (.txt)")'''


# -------------------------
# SINGLE FILE (Frontend)
# -------------------------
def process_single_audio(file_path):
    return transcribe_audio(file_path)


# -------------------------
# FLASK COMPATIBILITY
# -------------------------
def process_call_transcript(file_path):

    text = transcribe_audio(file_path)

    # ---- SAFETY CHECK ----
    if not text or text.strip() == "":
        return "No transcript available"

    return text



# -------------------------
# FOLDER BATCH (Dataset)
# -------------------------
def process_audio_folder(folder_path=AUDIO_FOLDER):

    results = []
    count = 1

    for file in os.listdir(folder_path):
        if file.endswith((".m4a", ".mp3", ".wav")):

            path = os.path.join(folder_path, file)
            print(f"Processing → {file}")

            text = transcribe_audio(path)

            out_file = os.path.join(
                OUTPUT_FOLDER,
                f"call_transcript_{count}.txt"
            )

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(text)

            results.append({"file": file, "transcript": text})
            count += 1

    print("\n✅ Audio transcripts saved")
    return results




if __name__ == "__main__":
    process_audio_folder()



