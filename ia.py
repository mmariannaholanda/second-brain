import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODELO = os.environ["GEMINI_MODEL"]


def resumir(texto):
    resposta = cliente.models.generate_content(
        model=MODELO,
        contents="Resuma em português, em tópicos curtos, o texto abaixo. "
                 "Não invente informações que não estejam nele.\n\n" + texto,
    )
    return resposta.text


if __name__ == "__main__":
    print(resumir("Um microcontrolador sozinho não tem corrente para alimentar vários servos, por isso se usa um driver."))