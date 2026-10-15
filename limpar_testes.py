import sqlite3



conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON")



# os dados de teste que o banco2.py inseria a cada execução
testes = conexao.execute(
    "SELECT id, tipo, titulo FROM materiais "
    "WHERE (tipo = 'anotacao' AND titulo = 'Minhas dúvidas' AND texto = 'não entendi Hooke') "
    "OR (tipo = 'arquivo' AND titulo = 'Slide aula 3' AND caminho_arquivo = 'uploads/s3.pdf')"
).fetchall()



print("Materiais de teste encontrados:")
for linha in testes:
    print(linha)



# PDFs seus enviados mais de uma vez (só mostra, não apaga nada)
repetidos = conexao.execute(
    "SELECT titulo, COUNT(*) FROM materiais WHERE tipo = 'arquivo' "
    "GROUP BY caminho_arquivo HAVING COUNT(*) > 1"
).fetchall()
# GROUP BY junta as linhas com o mesmo caminho; HAVING COUNT(*) > 1 → fica só quem aparece mais de uma vez

print("PDFs repetidos:", repetidos)



if testes and input("Apagar os materiais de teste? (s/n): ").lower() == "s":
    conexao.executemany("DELETE FROM materiais WHERE id = ?", [(id_,) for id_, _, _ in testes])
    conexao.commit()
    print("Apagados.")
else:
    print("Nada foi apagado.")



conexao.close()