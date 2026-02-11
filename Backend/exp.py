import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# This will print all models you have access to
for model in client.models.list():
    print(f"Model Name: {model.name} | Supported: {model.supported_actions}")