from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()
#print(os.getenv("HF_TOKEN"))


app = Flask(__name__)

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}"
}

@app.route("/summarize", methods=["POST"])
def summarize():
   
    '''#data = request.json
    #text = data["text"]

    # If you want to read from file instead of frontend, use this:
    #with open("../data/call log 1.txt", "r", encoding="utf-8") as f:
    #   text = f.read()

    payload = {
        "inputs": text,
        "parameters": {"max_length": 40}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    summary = result[0]["summary_text"]
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)'''

    try:
        # Get uploaded file
        uploaded_file = request.files.get("file")

        if not uploaded_file:
            return jsonify({"error": "No file uploaded"}), 400

        # Read file safely
        text = uploaded_file.read().decode("utf-8", errors="ignore").strip()

        # Empty check
        if len(text) == 0:
            return jsonify({"error": "File is empty"}), 400

        # Limit very large files
        text = text[:2000]

        # Prepare payload
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": 40,
                "min_length": 10
            }
        }

        # Send to HuggingFace
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({"error": response.text}), 500

        result = response.json()

        if not isinstance(result, list):
            return jsonify({"error": result})

        summary = result[0]["summary_text"]

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start server
if __name__ == "__main__":
    print("Server starting at http://127.0.0.1:5000")
    app.run(debug=True)
