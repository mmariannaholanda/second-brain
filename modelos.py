import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for modelo in cliente.models.list():
    if "generateContent" in (modelo.supported_actions or []):
        print(modelo.name)