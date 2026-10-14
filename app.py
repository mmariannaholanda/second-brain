import sqlite3                  # [Python] banco
from pathlib import Path
import streamlit as st          # [Streamlit] cria a página
from pypdf import PdfReader




st.title("Second Brain")        # [Streamlit] título da página

conexao = sqlite3.connect("secondbrain.db")


# Layout centralizado, fontes, cores, espaçamento, Menu de três pontinhos
# e configurações (tema, etc.)   - streamlit automatico




disciplinas = conexao.execute(
    "SELECT id, nome FROM disciplinas ORDER BY nome"
).fetchall()                    # [SQLite] lista de (id, nome)
if not disciplinas:
    st.info("Nenhuma disciplina ainda. Rode banco2.py.")
    st.stop()                   # [Streamlit] para o script aqui

ids = {nome: id_ for id_, nome in disciplinas}   # [Python] dicionário nome -> id


escolhida = st.selectbox("Disciplina", list(ids))  # [Streamlit] menu de escolha interativoo


# REGIAO PARA O UPLOAD DO ARQUIVO
arquivo = st.file_uploader("Enviar PDF para esta disciplina", type="pdf")

if arquivo is not None and st.button("Guardar e indexar"):
    pasta = Path("uploads")
    pasta.mkdir(exist_ok=True)
    destino = pasta / Path(arquivo.name).name     # .name descarta qualquer pasta no nome
    destino.write_bytes(arquivo.getbuffer())

    cursor = conexao.execute(
        "INSERT INTO materiais (disciplina_id, tipo, titulo, caminho_arquivo) "
        "VALUES (?, 'arquivo', ?, ?)",
        (ids[escolhida], destino.stem, str(destino)),
    )
    material_id = cursor.lastrowid

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS paginas (
            id INTEGER PRIMARY KEY,
            material_id INTEGER NOT NULL,
            numero INTEGER NOT NULL,
            texto TEXT NOT NULL,
            UNIQUE (material_id, numero),
            FOREIGN KEY (material_id) REFERENCES materiais (id)
        )
    """)
    for numero, pagina in enumerate(PdfReader(destino).pages, start=1):
        texto = " ".join((pagina.extract_text() or "").split())
        conexao.execute(
            "INSERT OR REPLACE INTO paginas (material_id, numero, texto) VALUES (?, ?, ?)",
            (material_id, numero, texto),
        )
    conexao.commit()
    st.rerun()
    
    
# LISTA DE MATERIAIS COM A CAIXINHA DE ENVIO PARA IA
materiais = conexao.execute(
    "SELECT id, titulo, tipo, enviar_para_ia FROM materiais WHERE disciplina_id = ? ORDER BY id",
    (ids[escolhida],),
).fetchall()


#materiais = conexao.execute(
 #   "SELECT id, titulo, tipo, enviar_para_ia FROM materiais "
  #  "WHERE disciplina_id = ? ORDER BY id",
 #   (ids[escolhida],),
#).fetchall()


for id_, titulo, tipo, marcado in materiais:
    novo = st.checkbox(                           # [Streamlit] caixinha que dá para marcarr
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