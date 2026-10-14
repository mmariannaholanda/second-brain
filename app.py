import sqlite3                  # [Python] banco
from pathlib import Path
import streamlit as st          # [Streamlit] cria a página
from pypdf import PdfReader




st.title("Second Brain")        # [Streamlit] título da página

conexao = sqlite3.connect("secondbrain.db")


# Layout centralizado, fontes, cores, espaçamento, Menu de três pontinhos
# e configurações (tema, etc.)   - streamlit automatico



# Implementar: nao poder carregar o mesmo pdf mais de uma vez, eu tbm n entendi pq ficar varios marcados dizendo 
# que é pra enviar tudo, sendo q a ia n vai resumir tudo de uma vez, e outra é que eu n consigo abrir o arquivo ao tocar no nome
# outra é que


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


materiais = conexao.execute(
    "SELECT id, titulo, tipo, enviar_para_ia FROM materiais "
    "WHERE disciplina_id = ? AND tipo = 'arquivo' ORDER BY id",
    (ids[escolhida],),
).fetchall()


for id_, titulo, tipo, marcado in materiais:
    novo = st.checkbox(                           # [Streamlit] caixinha que dá para marcarr
        f"{titulo} ({tipo})",
        value=bool(marcado),                      # começa como está no banco
        key=f"m{id_}",                            # nome único de cada caixinha
    )
    if novo != bool(marcado):                     # [Nosso] mudou? grava no banco
        conexao.execute(
            "UPDATE materiais SET enviar_para_ia = ? WHERE id = ?",
            (int(novo), id_),
        )
        conexao.commit()








# foco nos botões -------------------
st.divider()  # cria uma linha horizontal para separar partes da interface.
st.subheader("Resumos")


# criando a tabela dos resumos
conexao.execute("""
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



marcados = conexao.execute(
    "SELECT id, titulo FROM materiais "
    "WHERE disciplina_id = ? AND tipo = 'arquivo' AND enviar_para_ia = 1",
    (ids[escolhida],),
).fetchall()

if not marcados:
    st.caption("Marque um material acima para poder resumir.")

for id_, titulo in marcados:
    if st.button(f"Resumir: {titulo}", key=f"r{id_}"):  # key=f"r{id_}" → define uma identificação única para o botão, usando o valor de id_
        paginas = conexao.execute(
            "SELECT numero, texto FROM paginas WHERE material_id = ? ORDER BY numero",
            (id_,),
        ).fetchall()
        if not paginas:
            st.warning("Este material não tem páginas indexadas.")
        else:
            try:
                from ia import MODELO, resumir     # só carrega a IA aqui, depois do portão
                with st.spinner("Resumindo..."):
                    for numero, texto in paginas:
                        conexao.execute(
                            "INSERT OR REPLACE INTO resumos "
                            "(material_id, pagina_numero, texto, modelo) VALUES (?, ?, ?, ?)",
                            (id_, numero, resumir(texto), MODELO),
                        )
                        conexao.commit()
            except Exception as erro: # para tratar o erro, 
                st.error(f"Não foi possível resumir: {erro}")

    salvos = conexao.execute(
        "SELECT pagina_numero, texto FROM resumos WHERE material_id = ? ORDER BY pagina_numero",
        (id_,),
    ).fetchall()
    if salvos:
        with st.expander(f"Resumo de {titulo} ({len(salvos)} página(s))"):
            # st.expander() é um comando da biblioteca Streamlit que cria uma seção que pode
            # ser aberta ou fechada pelo usuário, como um menu retrátil

            for numero, texto in salvos:
                st.markdown(f"**Página {numero}**") 
                # st.markdown() é um comando da biblioteca Streamlit que permite exibir
                # textos usando formatação Markdown, como títulos, negrito, listas e links
                st.write(texto)




# Minhas anotações ------------------
st.divider()
st.subheader("Caderno")



with st.form("nova_nota", clear_on_submit=True):      # clear_on_submit limpa os campos após salvar
    titulo_nota = st.text_input("Título da anotação")
    texto_nota = st.text_area("Texto")
    salvar = st.form_submit_button("Salvar anotação")

# st.form() permite agrupar campos e botões em um formulário
# with → define quais comandos estarão dentro do formulário
# clear_on_submit=True → limpa os campos do formulário depois que ele é enviado



if salvar:
    if titulo_nota.strip():
        conexao.execute(
            "INSERT INTO materiais (disciplina_id, tipo, titulo, texto, enviar_para_ia) "
            "VALUES (?, 'anotacao', ?, ?, 0)",         # 0 fixo: anotação nunca vai para a IA
            (ids[escolhida], titulo_nota.strip(), texto_nota),
        )
        conexao.commit()
        st.rerun()
    else:
        st.warning("Dê um título à anotação.")

notas = conexao.execute(
    "SELECT titulo, texto FROM materiais WHERE disciplina_id = ? AND tipo = 'anotacao' ORDER BY id DESC",
    (ids[escolhida],),
).fetchall()

for titulo, texto in notas:
    with st.expander(titulo):
        # st.expander(titulo) → cria uma seção expansível
        st.write(texto)




# Gerador de prompt para outras IAs ------------------
st.divider()
st.subheader("Gerar prompt para outra IA")

arquivos = conexao.execute(
    "SELECT id, titulo FROM materiais WHERE disciplina_id = ? AND tipo = 'arquivo' ORDER BY id",
    (ids[escolhida],),
).fetchall()



if not arquivos:
    st.caption("Envie um PDF para poder gerar um prompt.")
else:
    titulos = {id_: titulo for id_, titulo in arquivos}          # id -> título
    material_prompt = st.selectbox(
        "Material de referência", list(titulos),
        format_func=lambda i: titulos[i], key="prompt_material",  # mostra o título, guarda o id
    )
    # list(titulos) Transforma titulos em uma lista
    # format_func=lambda i: titulos[i]; Significa: para cada identificador i,
    # consulte o dicionário titulos e mostre o título correspondente





    tema = st.text_input("Tema a estudar", key="prompt_tema")
    objetivo = st.text_input("Objetivo (ex.: prova, projeto, revisão)", key="prompt_objetivo")
    # st.text_input() cria um campo de texto no qual o usuário pode digitar alguma coisa
    
    nivel = st.selectbox("Nível de profundidade", ["Introdutório", "Intermediário", "Avançado"], key="prompt_nivel")
    incluir = st.checkbox("Incluir o texto do material no prompt", key="prompt_incluir")






    if tema.strip():
        partes = [
            f"Você é meu professor de {escolhida}.",
            f"Quero estudar: {tema.strip()}.",
            f"Objetivo: {objetivo.strip() or 'compreender o conteúdo'}.",
            f"Nível de profundidade: {nivel.lower()}.",
            f"Material de referência: {titulos[material_prompt]}.",
            "",
            "Como quero que você ensine:",
            "- Explique os conceitos antes das fórmulas, dizendo de onde cada fórmula vem e por que funciona.",
            "- Ensine passo a passo, sem pular etapas, conectando cada ideia ao que já foi explicado.",
            "- Dê exemplos simples e depois exercícios para eu praticar.",
            "- Baseie-se no material de referência. Não invente informações que ele não contém; se faltar algo, avise.",
        ]
        if incluir:
            try:
                paginas_prompt = conexao.execute(
                    "SELECT numero, texto FROM paginas WHERE material_id = ? ORDER BY numero",
                    (material_prompt,),
                ).fetchall()
                partes += ["", "Texto do material (extraído de PDF, fórmulas podem ter erros):"]
                partes += [f"[Página {n}] {t}" for n, t in paginas_prompt]
            except sqlite3.OperationalError:
                st.warning("Este material ainda não tem texto indexado.")
        st.code("\n".join(partes), language=None)