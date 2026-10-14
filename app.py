import sqlite3                  # [Python] banco
import streamlit as st          # [Streamlit] cria a página

st.title("Second Brain")        # [Streamlit] título da página

conexao = sqlite3.connect("secondbrain.db")

disciplinas = conexao.execute(
    "SELECT id, nome FROM disciplinas ORDER BY nome"
).fetchall()                    # [SQLite] lista de (id, nome)
if not disciplinas:
    st.info("Nenhuma disciplina ainda. Rode banco2.py.")
    st.stop()                   # [Streamlit] para o script aqui

ids = {nome: id_ for id_, nome in disciplinas}   # [Python] dicionário nome -> id
escolhida = st.selectbox("Disciplina", list(ids))  # [Streamlit] menu de escolha

materiais = conexao.execute(
    "SELECT id, titulo, tipo, enviar_para_ia FROM materiais "
    "WHERE disciplina_id = ? ORDER BY id",
    (ids[escolhida],),
).fetchall()

for id_, titulo, tipo, marcado in materiais:
    novo = st.checkbox(                           # [Streamlit] caixinha
        f"{titulo} ({tipo}): enviar para a IA",
        value=bool(marcado),                      # começa como está no banco
        key=f"m{id_}",                            # nome único de cada caixinha
    )
    if novo != bool(marcado):                     # [Nosso] mudou? grava no banco
        conexao.execute(
            "UPDATE materiais SET enviar_para_ia = ? WHERE id = ?",
            (int(novo), id_),
        )
        conexao.commit()