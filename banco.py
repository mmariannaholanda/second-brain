# CRIANDO O BANCO DE DADOS


import sqlite3

conexao = sqlite3.connect("secondbrain.db")  # .db é uma extensão de arquivo que significa Database
cursor = conexao.cursor()  # cursor é um objeto do Python que permite executar comandos SQL no banco de dados



# cursor.execute() é usado para executar um comando SQL no banco de dados
cursor.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE
    )
""")
# aqui em cima cria 2 colunas, a id e o nome



# insert add uma linha
cursor.execute("INSERT OR IGNORE INTO disciplinas (nome) VALUES (?)", ("Física",))
conexao.commit()

for linha in cursor.execute("SELECT id, nome FROM disciplinas"):
    print(linha)

conexao.close()