# Liga o enviar_para_ia de um material a partir de uma autorização
# a decisão do usuário muda enviar_para_ia de 0 para 1

import sqlite3
import sys

material_id = int(sys.argv[1])

conexao = sqlite3.connect("secondbrain.db")
cursor = conexao.execute(
    "UPDATE materiais SET enviar_para_ia = 1 WHERE id = ?", (material_id,)
)
conexao.commit()
print(f"{cursor.rowcount} material(is) marcado(s).")
# cursor.rowcount informa quantas linhas foram afetadas pelo último comando SQL executado pelo cursor


conexao.close()