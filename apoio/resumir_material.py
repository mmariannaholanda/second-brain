# Confere a autorização, pega as páginas, chama a IA e guarda o resumo

import sqlite3     
import sys                          # [Python] dá acesso aos argumentos e permite encerrar o programa


material_id = int(sys.argv[1])      # [Python] int() vira número






conexao = sqlite3.connect("secondbrain.db")   # [Python/SQLite] abre o arquivo do banco
conexao.execute("PRAGMA foreign_keys = ON")   # [SQLite] liga a checagem de chaves estrangeiras (vem desligada)
cursor = conexao.cursor()                     # [Python/SQLite] objeto que envia comandos SQL

cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumos (
        id INTEGER PRIMARY KEY,
        material_id INTEGER NOT NULL,
        pagina_numero INTEGER NOT NULL,
        texto TEXT NOT NULL,
        modelo TEXT NOT NULL,
        UNIQUE (material_id, pagina_numero),
        FOREIGN KEY (material_id) REFERENCES materiais (id)
    )
""")
# [SQLite] cria a tabela só se não existir. UNIQUE impede dois resumos da mesma página;
# FOREIGN KEY liga o resumo a um material que exista.




cursor.execute("SELECT enviar_para_ia FROM materiais WHERE id = ?", (material_id,))
linha = cursor.fetchone()           # [Python/SQLite] pega a primeira linha do resultado (ou None se não achou)
if linha is None:
    sys.exit("Material não encontrado.")
if linha[0] != 1:
    sys.exit("Este material não está marcado para a IA.")      # [Nosso] o portão de privacidade




paginas = cursor.execute(
    "SELECT numero, texto FROM paginas WHERE material_id = ? ORDER BY numero",
    (material_id,),
).fetchall()                        # [SQLite] busca as páginas em ordem; fetchall() devolve todas como lista
if not paginas:
    sys.exit("Sem páginas indexadas. Rode indexar.py primeiro.")



from ia import MODELO, resumir      # [Nosso] traz do ia.py o nome do modelo e a função que fala com a IA



for numero, texto in paginas:       # [Python] repete para cada página, separando número e texto
    resumo = resumir(texto)         # [Gemini] a chamada que sai para a IA (feita dentro do ia.py)
    cursor.execute(
        "INSERT OR REPLACE INTO resumos (material_id, pagina_numero, texto, modelo) VALUES (?, ?, ?, ?)",
        (material_id, numero, resumo, MODELO),
    )                               # [SQLite] grava o resumo; REPLACE atualiza se já existir
    conexao.commit()                # [SQLite] confirma a gravação a cada página (se falhar na 5, as 4 primeiras ficam)
    print(f"--- página {numero} ---")   # [Python] f"..." coloca o valor da variável dentro do texto
    print(resumo)

conexao.close()                     # [Python/SQLite] fecha o banco