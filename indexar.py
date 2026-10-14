# abre a caixa uma vez só e guarda o conteúdo no banco, página por página
# isso é útil para que a IA não precise abrir o PDF toda vez que for consultar o conteúdo


# transformar o conteúdo de um arquivo em dados que o banco consegue
# consultar, como o índice no fim de um livro, que te leva direto ao assunto sem folhear tudo


import sqlite3
import sys
from pypdf import PdfReader

material_id = int(sys.argv[1])

conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS paginas (
        id INTEGER PRIMARY KEY,
        material_id INTEGER NOT NULL,
        numero INTEGER NOT NULL,
        texto TEXT NOT NULL,
        UNIQUE (material_id, numero),
        FOREIGN KEY (material_id) REFERENCES materiais (id)
    )
""")

cursor.execute("SELECT caminho_arquivo FROM materiais WHERE id = ?", (material_id,))
linha = cursor.fetchone()
if linha is None:
    sys.exit("Material não encontrado.")

leitor = PdfReader(linha[0])
for numero, pagina in enumerate(leitor.pages, start=1):
    texto = " ".join((pagina.extract_text() or "").split())
    cursor.execute(
        "INSERT OR REPLACE INTO paginas (material_id, numero, texto) VALUES (?, ?, ?)",
        (material_id, numero, texto),
    )

conexao.commit()
conexao.close()
print(f"{len(leitor.pages)} página(s) indexada(s).")