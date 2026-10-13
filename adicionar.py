import shutil # manipular arquivos e pastas, como copiar, mover e excluir arquivos
import sqlite3 # criar e acessar bancos de dados SQLite, como o secondbrain.db
import sys # acessar informações e recursos do Python, como argumentos passados ao executar o programa
from pathlib import Path # trabalhar com caminhos de arquivos e pastas de forma prática



# python disponibiliza os argumentos em uma lista chamada de sys.argv
# e a psoicao é dada na hora em que o arquivo é chamado pela ordem em que os arg aparecem
origem = Path(sys.argv[1])          # arquivo que você quer guardar
disciplina = sys.argv[2]            # nome da disciplina

pasta = Path("uploads")  # path pega o caminho da pasta uploads
pasta.mkdir(exist_ok=True) # mkdir cria a pasta no computador
destino = pasta / origem.name
shutil.copy(origem, destino)

conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

cursor.execute("SELECT id FROM disciplinas WHERE nome = ?", (disciplina,))
linha = cursor.fetchone()
if linha is None:
    sys.exit(f"Disciplina '{disciplina}' não existe.")

cursor.execute(
    "INSERT INTO materiais (disciplina_id, tipo, titulo, caminho_arquivo) VALUES (?, 'arquivo', ?, ?)",
    (linha[0], origem.stem, str(destino)),
)
conexao.commit()
conexao.close()
print("Guardado:", destino)