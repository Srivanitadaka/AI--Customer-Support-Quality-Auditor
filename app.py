from analyzer import analyze_text  
from flask import Flask, render_template, request, jsonify
import os
from transcription.chat_processor import process_chat_file
from transcription.deepgram_processor import process_call_transcript

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze_ajax", methods=["POST"])
def analyze_ajax():
    file = request.files.get("file")
    if not file:
        return jsonify({"summary": "No file uploaded"}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    print(f"📁 Processing: {filename}")
    
    try:
        # ✅ SMART DETECTION: Check if looks like audio or text
        is_audio_file = filename.lower().endswith((".m4a", ".mp3", ".wav"))
        is_chat_file = filename.lower().endswith(".txt") or filename.lower().endswith(".json")
        
        # READ FIRST 500 BYTES to detect content
        with open(filepath, "rb") as f:
            preview = f.read(500).decode('utf-8', errors='ignore')
        
        # If contains readable text → treat as chat
        has_readable_text = any(char.isalpha() for char in preview[:100]) and len(preview.strip()) > 10
        
        print(f"📊 Detection: audio={is_audio_file}, chat={is_chat_file}, text_detected={has_readable_text}")
        
        if is_audio_file:
            # Real audio files
            transcript = process_call_transcript(filepath)
            result = analyze_text(transcript)
            
        elif has_readable_text or is_chat_file:
            # ✅ TXT/JSON chats - read as TEXT
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            print(f"💬 Chat preview: {content[:100]}...")
            result = analyze_text(content)
            
        else:
            return jsonify({"summary": "Unsupported file format"}), 400
        
        print(f"✅ SUMMARY: {result['summary'][:100]}...")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({"summary": f"Error: {str(e)}"}), 500

        

if __name__ == "__main__":
    print("🚀 Server starting on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1')
