# IA não recebe pdf, ela so recebe o texto do pdf, então é necessário
#  extrair o texto do pdf antes de enviar para a IA

# Bibliotecas como a pypdf reconstroem o texto a partir disso.
# Limitação importante: PDFs escaneados (foto de página) não têm texto nenhum,
# e fórmulas costumam sair bagunçadas. É por isso que, no seu documento, 
# as fórmulas extraídas precisam de revisão


import sys
from pypdf import PdfReader

leitor = PdfReader(sys.argv[1])
print("Páginas:", len(leitor.pages))

for numero, pagina in enumerate(leitor.pages, start=1):
    texto = pagina.extract_text() or ""
    # or "" evita erro quando a página não tem texto
    print(f"- página {numero} ({len(texto)} caracteres). ")

    limpo = " ".join(texto.split())
    # texto.split() quebra o texto em palavras,
    # descartando qualquer espaço ou quebra de linha repetidos

    print(limpo[:300])
    # limpo[:300] mostra só os primeiros 300 caracteres

