# Cria o banco e as tabelas base.
# Cria: disciplinas (id, nome único).
# Cria: materiais (disciplina_id, tipo, titulo, caminho_arquivo, texto, enviar_para_ia).
# Insere a disciplina "Física" (ignora se já existir).
# Insere 2 materiais de teste. Cada execução repete esses 2.
# Lê: materiais marcados para a IA (enviar_para_ia = 1).


import sqlite3

conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON")  # PRAGMA foreign_keys = ON	Ativa a verificação das chaves estrangeiras - id
cursor = conexao.cursor() # conexao.cursor()	Cria o cursor, usado para executar comandos SQL





# cursor.execute = para mandar uma instrução para o banco de dados executar


# cria a tabela 1: disciplinas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL UNIQUE
    )
""")


# cria a tabela 2: materiais
cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY,
        disciplina_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK (tipo IN ('arquivo', 'anotacao')),
        titulo TEXT NOT NULL,
        caminho_arquivo TEXT,
        texto TEXT,
        enviar_para_ia INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
    )
""")
# FOREIGN KEY: relaciona o material à tabela de disciplinas
# DEFAULT 0: define 0 automaticamente se nenhum valor for informado





# cadastro da disciplina
cursor.execute("INSERT OR IGNORE INTO disciplinas (nome) VALUES (?)", ("Física",))
conexao.commit()

# cadastro dos materiais
cursor.execute(
    "INSERT INTO materiais (disciplina_id, tipo, titulo, texto, enviar_para_ia) VALUES (?, ?, ?, ?, ?)",
    (disc_id, "anotacao", "Minhas dúvidas", "não entendi Hooke", 0),
)
# disc_id: guarda o ID de Física para usar nos materiais
# valor 0 indica que ela não será enviada para a IA






# busca do ID da disciplina
cursor.execute("SELECT id FROM disciplinas WHERE nome = ?", ("Física",))
disc_id = cursor.fetchone()[0]
# cursor.fetchone()[0] serve para pegar o primeiro resultado de uma consulta ao banco de dados





# cadastro 2- indica que serao arquivos pdf
cursor.execute(
    "INSERT INTO materiais (disciplina_id, tipo, titulo, caminho_arquivo, enviar_para_ia) VALUES (?, ?, ?, ?, ?)",
    (disc_id, "arquivo", "Slide aula 3", "uploads/s3.pdf", 1),
)
conexao.commit()







# mostrar os materiais selecionados para a IA
for linha in cursor.execute("SELECT titulo, tipo FROM materiais WHERE enviar_para_ia = 1"):
    print(linha)


# fechando o banco
conexao.close()