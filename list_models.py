import os
from google import genai

try:
    client = genai.Client()
    print("--- Modelos Disponibles para tu API Key ---")
    for m in client.models.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
