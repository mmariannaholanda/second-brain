# Mostra o que está no banco.
# Lê: materiais (id e título).
# Lê: paginas (primeiros 80 caracteres).
# Não altera nada.
# Dá erro se paginas ainda não existir. Rode indexar.py antes.

import sqlite3

conexao = sqlite3.connect("secondbrain.db")

print("MATERIAIS")
for linha in conexao.execute("SELECT id, titulo FROM materiais"):
    print(linha)

print("PAGINAS")
for linha in conexao.execute("SELECT material_id, numero, substr(texto, 1, 80) FROM paginas"):  # pega os primeiros 80 caracteres do texto armazenado na coluna texto
    print(linha)

conexao.close()