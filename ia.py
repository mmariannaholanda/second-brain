# Único arquivo que fala com o Gemini.
# Lê GEMINI_API_KEY e GEMINI_MODEL do arquivo .env.
# Função resumir(texto): envia o texto e devolve o resumo.
# Para trocar de provedor, mude só este arquivo.




import os
from dotenv import load_dotenv
from google import genai



load_dotenv()
# load_dotenv() é uma função da biblioteca python-dotenv que carrega as variáveis de ambiente
# de um arquivo chamado .env para que o Python consiga usar



cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODELO = os.environ["GEMINI_MODEL"]


def resumir(texto):
    resposta = cliente.models.generate_content(
        # cliente.models.generate_content() é um método usado para
        # enviar um conteúdo para um modelo de inteligência artificial generativa e receber uma resposta
        model=MODELO,
        contents="Resuma em português, em tópicos curtos, o texto abaixo. "
                 "Não invente informações que não estejam nele: \n\n" + texto,
    )
    return resposta.text


if __name__ == "__main__":
    print(resumir("Um microcontrolador sozinho não tem corrente para alimentar vários servos, por isso se usa um driver."))