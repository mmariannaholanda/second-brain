# Cria o banco e as tabelas base.
# Cria: disciplinas (id, nome único).
# Cria: materiais (disciplina_id, tipo, titulo, caminho_arquivo, texto, enviar_para_ia).
# Insere a disciplina "Física" (ignora se já existir).
# As outras tabelas (paginas, resumos, topicos) são criadas pelo app.py.



import sqlite3



conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON")     # liga a checagem de chaves estrangeiras (o SQLite vem com ela desligada)
cursor = conexao.cursor()



cursor.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE
    )
""")



cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY,
        disciplina_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('arquivo', 'anotacao')),
        titulo TEXT NOT NULL,
        caminho_arquivo TEXT,
        texto TEXT,
        enviar_para_ia INTEGER NOT NULL DEFAULT 0,
        hash_arquivo TEXT,
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
    )
""")



cursor.execute("INSERT OR IGNORE INTO disciplinas (nome) VALUES (?)", ("Física",))
# OR IGNORE → se "Física" já existe, o UNIQUE recusa e o banco pula, sem duplicar



conexao.commit()
conexao.close()
print("Banco prontinho")