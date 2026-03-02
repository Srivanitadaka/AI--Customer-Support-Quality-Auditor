from flask import Flask, render_template, request, jsonify
import os, json
from pathlib import Path
from analyzer import analyze_text

app = Flask(__name__, static_folder="static", template_folder="templates")
UPLOAD_FOLDER  = "uploads"
RESULTS_FOLDER = Path(__file__).resolve().parent / "analysis_results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-store"
    return r

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze_ajax", methods=["POST"])
def analyze_ajax():
    file = request.files.get("file")
    if not file:
        return jsonify({"summary":"No file uploaded"}), 400
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    print(f"\n📁 Processing: {filename}")
    try:
        is_audio = filename.lower().endswith((".m4a",".mp3",".wav",".mp4",".flac"))
        is_text  = filename.lower().endswith((".txt",".json"))
        with open(filepath,"rb") as f:
            preview = f.read(200).decode("utf-8",errors="ignore")
        has_text = any(c.isalpha() for c in preview[:100]) and len(preview.strip())>10
        if is_audio:
            try:
                from transcription.deepgram_processor import process_call_transcript
                transcript = process_call_transcript(filepath)
                if not transcript or len(transcript.strip())<20 or "failed" in transcript.lower():
                    return jsonify({"summary":f"Transcription issue: {transcript[:150]}","grade":"N/A","overall_score":0,"scores":{},"dimension_scores":{},"satisfaction":{},"agent_quality":{},"model_metrics":{},"violations":[],"improvements":[],"highlights":[],"sentiment":"unknown","issue_detected":"Transcription error","was_resolved":False,"call_outcome":"Unresolved"}), 200
                result = analyze_text(transcript)
            except Exception as e:
                return jsonify({"summary":f"Audio error: {str(e)[:150]}","grade":"N/A","overall_score":0,"scores":{},"dimension_scores":{},"satisfaction":{},"agent_quality":{},"model_metrics":{},"violations":[],"improvements":[],"highlights":[],"sentiment":"unknown","issue_detected":"Audio error","was_resolved":False,"call_outcome":"Unresolved"}), 200
        elif is_text or has_text:
            with open(filepath,"r",encoding="utf-8") as f:
                content = f.read()
            result = analyze_text(content)
        else:
            return jsonify({"summary":"Unsupported format."}), 400
        out_path = RESULTS_FOLDER / f"scored_{Path(filename).stem}.json"
        with open(out_path,"w",encoding="utf-8") as f:
            json.dump({**result,"_source":filename,"_type":"live_upload"},f,indent=2)
        print(f"✅ Grade: {result.get('grade')} | Score: {result.get('overall_score')}/100")
        return jsonify(result)
    except Exception as e:
        print(f"❌ {e}")
        return jsonify({"summary":f"Server error: {str(e)[:150]}"}), 500

@app.route("/results")
def get_results():
    results = []
    for f in sorted(RESULTS_FOLDER.glob("scored_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sat  = data.get("satisfaction", {})
            results.append({
                "filename":           f.stem.replace("scored_",""),
                "grade":              data.get("grade","?"),
                "overall_score":      data.get("overall_score",0),
                "sentiment":          data.get("sentiment","unknown"),
                "was_resolved":       data.get("was_resolved",False),
                "call_outcome":       data.get("call_outcome","Unresolved"),
                "issue_detected":     data.get("issue_detected","—"),
                "summary":            data.get("summary",""),
                "violations":         len(data.get("violations",[])),
                "scores":             data.get("dimension_scores", data.get("scores",{})),
                "satisfaction_rating":sat.get("rating",0),
                "satisfaction":       sat,
                "_type":              data.get("_type","batch"),
                "_source":            data.get("_source",f.stem)
            })
        except: pass
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return jsonify(results)

if __name__ == "__main__":
    print("🚀 Server starting on http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1")