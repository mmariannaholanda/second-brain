# Lista os modelos do Gemini que a sua chave pode usar.
# Serve para escolher o nome do GEMINI_MODEL no .env.
# Não usa o banco de dados.

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for modelo in cliente.models.list():
    if "generateContent" in (modelo.supported_actions or []):
        print(modelo.name)