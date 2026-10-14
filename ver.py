import sqlite3

conexao = sqlite3.connect("secondbrain.db")

print("MATERIAIS")
for linha in conexao.execute("SELECT id, titulo FROM materiais"):
    print(linha)

print("PAGINAS")
for linha in conexao.execute("SELECT material_id, numero, substr(texto, 1, 80) FROM paginas"):
    print(linha)

conexao.close()