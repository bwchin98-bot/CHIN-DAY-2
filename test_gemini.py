import os
import json
import google.generativeai as genai

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config.get("GEMINI_API_KEY", "")
print("API Key loaded:", api_key[:10] + "..." if api_key else "None")

try:
    genai.configure(api_key=api_key)
    print("Listing models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error listing models:", e)

