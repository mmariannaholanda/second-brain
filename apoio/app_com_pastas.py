import sqlite3                  # [Python] banco
from pathlib import Path
import streamlit as st          # [Streamlit] cria a página
import hashlib                # vai dar pra trazer uma impressão digital do conteudo
from pypdf import PdfReader


st.title("Second Brain")        # [Streamlit] título da página

conexao = sqlite3.connect("secondbrain.db")
conexao.execute("PRAGMA foreign_keys = ON") 

# Layout centralizado, fontes, cores, espaçamento, Menu de três pontinhos
# e configurações (tema, etc.)   - streamlit automatico






# cadastro de semestres ===============================================
conexao.execute("""
    CREATE TABLE IF NOT EXISTS semestres (
        id INTEGER PRIMARY KEY,
        nome_semestre TEXT NOT NULL,
        UNIQUE (nome_semestre)
    )
""")

# add semestre_id a tabela de disciplinas
colunas = [
    linha[1]
    for linha in conexao.execute("PRAGMA table_info(disciplinas)")
]
if "semestre_id" not in colunas:
    conexao.execute("""
        ALTER TABLE disciplinas
        ADD COLUMN semestre_id INTEGER REFERENCES semestres(id)
    """)

conexao.commit()







# MIGRAÇÃO: coluna hash_arquivo

# o código pergunta ao banco quais colunas a tabela tem e só cria a nova se ela não estiver na lista - linha[1] é o nome da coluna, linha[0] é o número da coluna (0, 1, 2, ...)
colunas = [linha[1] for linha in conexao.execute("PRAGMA table_info(materiais)")]
if "hash_arquivo" not in colunas:       # só altera a tabela se a coluna ainda não existir
    conexao.execute("ALTER TABLE materiais ADD COLUMN hash_arquivo TEXT")
    conexao.commit()




# calcula o hash dos PDFs que já estavam guardados
sem_hash = conexao.execute(
    "SELECT id, caminho_arquivo FROM materiais "
    "WHERE tipo = 'arquivo' AND hash_arquivo IS NULL AND caminho_arquivo IS NOT NULL"
).fetchall()



# vamos pegar cada PDF que não tem hash, calcular o hash e gravar no banco
for id_, caminho in sem_hash:
    if Path(caminho).exists():
         
        hash_antigo = hashlib.sha256(Path(caminho).read_bytes()).hexdigest()
        # Path para representar esse caminho de forma que o Python consiga trabalhar com o arquivo
        # read_bytes() lê o conteúdo do arquivo como bytes
        # sha256() calcula um hash criptográfico usando o algoritmo SHA-256 - imopressao digital do conteudo
        # .hexdigest(): transforma o resultado em texto

        conexao.execute("UPDATE materiais SET hash_arquivo = ? WHERE id = ?", (hash_antigo, id_))
conexao.commit()




# a trava do banco: não pode haver dois PDFs com o mesmo hash na mesma disciplina
try:
    conexao.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_material_hash ON materiais (disciplina_id, hash_arquivo)"
    )
    # idx é uma convenção comum para indicar que um objeto do banco de dados é um índice
    # Ela informa ao SQLite quais colunas devem compor o índice (INDEX) 
    # Ele verifica se já existe um registro com o mesmo disciplina_id E o mesmo hash_arquivo

    conexao.commit()
except sqlite3.IntegrityError:
    st.warning("Já existem PDFs repetidos no banco. Remova as cópias para ativar a trava.")







# seleção ou cadastro de semestres ====================================
escolheu_algum_semestre = False
disciplina_id = None

semestres = conexao.execute(
    "SELECT id, nome_semestre FROM semestres ORDER BY nome_semestre"
).fetchall()                         # [SQLite] lista de (id, nome_semestre)

ids_semestres = {
    nome_semestre: id_
    for id_, nome_semestre in semestres
}                                   # [Python] dicionário nome -> id

opcoes_semestres = list(ids_semestres.keys()) + ["+ Criar novo semestre"]

semestre_escolhido = st.selectbox(
    "Semestre",
    opcoes_semestres,
    index=None,
    placeholder="Selecione um semestre"
)

if semestre_escolhido == "+ Criar novo semestre":

    novo_semestre = st.text_input("Nome do novo semestre")

    if st.button("Criar semestre"):

        if not novo_semestre.strip():
            st.warning("Digite um nome válido para o semestre.")

        elif conexao.execute(
            "SELECT id FROM semestres WHERE nome_semestre = ?",
            (novo_semestre.strip(),)
        ).fetchone():
            st.warning("Esse semestre já está cadastrado.")

        else:
            conexao.execute(
                "INSERT INTO semestres (nome_semestre) VALUES (?)",
                (novo_semestre.strip(),)
            )
            conexao.commit()
            st.success(f"Semestre '{novo_semestre.strip()}' criado.")
            st.rerun()              # [Streamlit] recarrega a página

elif semestre_escolhido is not None:

    semestre_id = ids_semestres[semestre_escolhido]
    escolheu_algum_semestre = True


# seleção ou cadastro de disciplinas ==================================
if escolheu_algum_semestre:

    # Busca somente as disciplinas do semestre escolhido
    disciplinas = conexao.execute(
        """
        SELECT id, nome
        FROM disciplinas
        WHERE semestre_id = ?
        ORDER BY nome
        """,
        (semestre_id,)
    ).fetchall()                    # [SQLite] lista de (id, nome)

    ids_disciplinas = {
        nome: id_
        for id_, nome in disciplinas
    }                               # [Python] dicionário nome -> id

    opcoes_disciplinas = (
        list(ids_disciplinas.keys()) + ["+ Criar nova disciplina"]
    )

    disciplina_escolhida = st.selectbox(
        "Disciplina",
        opcoes_disciplinas,
        index=None,
        placeholder="Selecione uma disciplina"
    )

    if disciplina_escolhida == "+ Criar nova disciplina":

        nova_disciplina = st.text_input("Nome da nova disciplina")

        if st.button("Cadastrar disciplina"):

            if not nova_disciplina.strip():
                st.warning("Digite um nome válido.")

            elif conexao.execute(
                """
                SELECT id
                FROM disciplinas
                WHERE nome = ? AND semestre_id = ?
                """,
                (nova_disciplina.strip(), semestre_id)
            ).fetchone():
                st.warning("Essa disciplina já existe neste semestre.")

            else:
                conexao.execute(
                    """
                    INSERT INTO disciplinas (nome, semestre_id)
                    VALUES (?, ?)
                    """,
                    (nova_disciplina.strip(), semestre_id)
                )
                conexao.commit()
                st.success("Disciplina cadastrada!")
                st.rerun()          # [Streamlit] atualiza a lista

    elif disciplina_escolhida is not None:

        disciplina_id = ids_disciplinas[disciplina_escolhida]
        st.write(f"Disciplina selecionada: {disciplina_escolhida}")











# Upload do arquivo ====================================================

if escolheu_algum_semestre and disciplina_escolhida is not None and disciplina_escolhida != "+ Criar nova disciplina":

    arquivo = st.file_uploader("Enviar PDF para esta disciplina", type="pdf")

    if arquivo is not None and st.button("Guardar e indexar"):

        # Calcula a impressão digital do conteúdo do PDF enviado.
        conteudo = arquivo.getbuffer()
        hash_novo = hashlib.sha256(conteudo).hexdigest()      # impressão digital do conteúdo do PDF

        # O SQL procura um registro que tenha a mesma disciplina e o mesmo hash
        ja_existe = conexao.execute(
            "SELECT titulo FROM materiais WHERE disciplina_id = ? AND hash_arquivo = ?",
            (disciplina_id, hash_novo),
        ).fetchone()

        # cria a pasta uploads se não existir e define o caminho do arquivo de destino
        pasta = Path("uploads")
        pasta.mkdir(exist_ok=True)
        destino = pasta / Path(arquivo.name).name     # .name descarta qualquer pasta no nome

        # mesmo nome, mesmo conteúdo → não precisa gravar de novo
        if ja_existe:
            st.warning(f"Este PDF já foi enviado como '{ja_existe[0]}'.")

        elif destino.exists():
            # mesmo nome, conteúdo diferente → gravar por cima apagaria o arquivo do outro material
            st.warning("Já existe um arquivo com esse nome em uploads, com outro conteúdo. Renomeie o PDF e envie de novo.")

        else:
            destino.write_bytes(conteudo)

            cursor = conexao.execute(
                "INSERT INTO materiais (disciplina_id, tipo, titulo, caminho_arquivo, hash_arquivo) "
                "VALUES (?, 'arquivo', ?, ?, ?)",
                (disciplina_id, destino.stem, str(destino), hash_novo),
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
            st.success("PDF guardado e indexado!")
            st.rerun()

else:
    st.info("Selecione um semestre e uma disciplina para enviar um PDF.")



if disciplina_id is None:
    st.stop()














    
# LISTA DE MATERIAIS COM A CAIXINHA DE ENVIO PARA IA
materiais = conexao.execute(
    "SELECT id, titulo, tipo, enviar_para_ia FROM materiais "
    "WHERE disciplina_id = ? AND tipo = 'arquivo' ORDER BY id",
    (disciplina_id,),
).fetchall()






for id_, titulo, tipo, marcado in materiais:
    novo = st.checkbox(                           # [Streamlit] caixinha que dá para marcarr
        f"Permitir envio à IA: {titulo}",
        value=bool(marcado),                      # começa como está no banco
        key=f"m{id_}",                            # nome único de cada caixinha
        help="Marcar só libera os botões de resumir e extrair tópicos. Nada é enviado até você clicar em um deles.",
        # help → mostra um balãozinho de ajuda ao passar o mouse sobre o ponto de interrogação
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
    (disciplina_id,),
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
            (disciplina_id, titulo_nota.strip(), texto_nota),
        )
        conexao.commit()
        st.rerun()
    else:
        st.warning("Dê um título à anotação.")

notas = conexao.execute(
    "SELECT titulo, texto FROM materiais WHERE disciplina_id = ? AND tipo = 'anotacao' ORDER BY id DESC",
    (disciplina_id,),
).fetchall()

for titulo, texto in notas:
    with st.expander(titulo):
        # st.expander(titulo) → cria uma seção expansível
        st.write(texto)












# Gerador de prompt para outras IAs ------------------
st.divider()
st.subheader("Gerar prompt para outra IA de resumo e ensino")

arquivos = conexao.execute(
    "SELECT id, titulo FROM materiais WHERE disciplina_id = ? AND tipo = 'arquivo' ORDER BY id",
    (disciplina_id,),
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
            f"Você é meu professor de {disciplina_escolhida}.",
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











# gerar prompt tópicos importantes ------------------
st.divider()
st.subheader("Mapa de tópicos")



# criando a tabela dos tópicos
conexao.execute("""
    CREATE TABLE IF NOT EXISTS topicos (
        id INTEGER PRIMARY KEY,
        material_id INTEGER NOT NULL UNIQUE,
        texto TEXT NOT NULL,
        modelo TEXT NOT NULL,
        FOREIGN KEY (material_id) REFERENCES materiais (id)
    )
""")
# UNIQUE em material_id → cada material só pode ter um mapa de tópicos
# se extrair de novo, o INSERT OR REPLACE troca o antigo pelo novo



if not marcados:
    st.caption("Marque \"Permitir envio à IA\" em um material acima para poder resumir.")

for id_, titulo in marcados:    # marcados vem da parte dos Resumos: só entram materiais com a caixinha marcada
    if st.button(f"Extrair tópicos: {titulo}", key=f"t{id_}"):   # key=f"t{id_}" → identificação única, diferente da do botão de resumir (r{id_})
        paginas_topicos = conexao.execute(
            "SELECT numero, texto FROM paginas WHERE material_id = ? ORDER BY numero",
            (id_,),
        ).fetchall()
        if not paginas_topicos:
            st.warning("Este material não tem páginas indexadas.")
        else:
            try:
                from ia import MODELO, topicos     # só carrega a IA aqui, depois do portão


                texto_completo = "\n".join(f"[Página {n}] {t}" for n, t in paginas_topicos)
                # "\n".join(...) junta todas as páginas em um texto só, uma embaixo da outra
                # o [Página N] na frente é o que permite a IA citar a origem de cada tópico


                with st.spinner("Extraindo tópicos..."):
                    # st.spinner() mostra uma mensagem de carregamento enquanto o bloco abaixo roda
                    resultado = topicos(texto_completo)
                conexao.execute(
                    "INSERT OR REPLACE INTO topicos (material_id, texto, modelo) VALUES (?, ?, ?)",
                    (id_, resultado, MODELO),
                )
                conexao.commit()
            except Exception as erro:   # para tratar o erro, sem derrubar a página
                st.error(f"Não foi possível extrair: {erro}")

    salvo = conexao.execute(
        "SELECT texto FROM topicos WHERE material_id = ?",
        (id_,),
    ).fetchone()
    # fetchone() devolve só a primeira linha do resultado (ou None se não achou nada)
    if salvo:
        with st.expander(f"Tópicos de {titulo}"):
            st.markdown(salvo[0])    # salvo[0] → primeira coluna da linha, que é o texto dos tópicos











# Gerar prompt de estudo por tópicos ------------------
st.divider()
st.subheader("Gerar prompt de estudo por tópicos")



com_topicos = conexao.execute(
    "SELECT m.id, m.titulo, t.texto FROM topicos t "
    "JOIN materiais m ON m.id = t.material_id "
    "WHERE m.disciplina_id = ? ORDER BY m.id",
    (disciplina_id,),
).fetchall()
# JOIN junta duas tabelas: aqui liga cada mapa de tópicos ao material de onde ele veio
# assim dá para mostrar o título do material junto com o texto dos tópicos



if not com_topicos:
    st.caption("Extraia os tópicos de um material marcado para gerar este prompt.")
else:
    mapa_topicos = {id_: (titulo, texto) for id_, titulo, texto in com_topicos}    # id -> (título, tópicos)
    material_topicos = st.selectbox(
        "Material de referência", list(mapa_topicos),
        format_func=lambda i: mapa_topicos[i][0], key="topicos_material",  # mostra o título, guarda o id
    )





    objetivo_topicos = st.text_input("Objetivo (ex.: prova, projeto, revisão)", key="topicos_objetivo")
    nivel_topicos = st.selectbox(
        "Nível de profundidade",
        ["Introdutório", "Intermediário", "Avançado", "De acordo com o do PDF"],
        key="topicos_nivel",
    )





    partes_topicos = [
        f"Você é meu professor de {disciplina_escolhida}.",
        f"Objetivo: {objetivo_topicos.strip() or 'compreender o conteúdo'}.",
        f"Nível de profundidade: {nivel_topicos.lower()}.",
        f"Material de referência: {mapa_topicos[material_topicos][0]}.",
        "",
        "Abaixo está o mapa de tópicos do material. Ensine cada tópico individualmente, em ordem.",
        "- Explique os conceitos antes das fórmulas, dizendo de onde cada fórmula vem e por que funciona.",
        "- Ensine passo a passo, sem pular etapas, e depois dê exemplos e exercícios.",
        "- Não invente informações que o mapa não contém; se faltar algo, avise.",
        "",
        "MAPA DE TÓPICOS:",
        mapa_topicos[material_topicos][1],
    ]
    st.code("\n".join(partes_topicos), language=None)
    # st.code() mostra o texto dentro de uma caixa, com um botão de copiar no canto
    # "\n".join(partes_topicos) → junta a lista de linhas em um texto só, com quebra de linha entre elas





# busca por palavras-chave ------------------
st.divider()
st.subheader("Buscar")

consulta = st.text_input("Buscar nos materiais e anotações", key="busca_texto")

if consulta.strip():
    try:



        # tokenize = 'unicode61 remove_diacritics 2'determina como o FTS5 separa e normaliza os termos durante a
        # indexação e a pesquisa --- unicode61 É o tokenizador que trata o texto como Unicode, permitindo lidar com caracteres especiais e acentos.
        # remove_diacritics 2 Remove os diacríticos (acentos) dos caracteres, tornando a busca mais flexível.
        # FTS5 é um recurso do SQLite que permite criar uma tabela virtual otimizada para buscas de texto completo.
        # Ele cria um índice de palavras que facilita a pesquisa rápida em grandes volumes de texto.
        conexao.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS busca USING fts5(
                disciplina UNINDEXED, titulo, texto, tipo UNINDEXED, pagina UNINDEXED,
                tokenize = 'unicode61 remove_diacritics 2'
            )
        """)




        # Reconstrói o índice a partir das tabelas reais (simples; ok para poucos dados)
        conexao.execute("DELETE FROM busca")
        conexao.execute("""
            INSERT INTO busca (disciplina, titulo, texto, tipo, pagina)
            SELECT d.nome, m.titulo, p.texto, 'arquivo', p.numero
            FROM paginas p
            JOIN materiais m ON m.id = p.material_id
            JOIN disciplinas d ON d.id = m.disciplina_id
        """)
        conexao.execute("""
            INSERT INTO busca (disciplina, titulo, texto, tipo, pagina)
            SELECT d.nome, m.titulo, COALESCE(m.texto, ''), 'anotacao', NULL
            FROM materiais m
            JOIN disciplinas d ON d.id = m.disciplina_id
            WHERE m.tipo = 'anotacao'
        """)
        conexao.commit()




        # Cada palavra vira "palavra"* : entre aspas (evita erro de sintaxe) e com * (aceita prefixo)
        termos = ['"' + palavra.replace('"', '') + '"*' for palavra in consulta.split()]
        resultados = conexao.execute(
            "SELECT disciplina, titulo, tipo, pagina, snippet(busca, 2, '**', '**', '…', 15) "
            "FROM busca WHERE busca MATCH ? ORDER BY rank LIMIT 20",
            (" ".join(termos),),
        ).fetchall()
    except sqlite3.OperationalError as erro:
        st.error(f"Não foi possível buscar: {erro}")
        resultados = []

    if not resultados:
        st.caption("Nada encontrado.")
    for disciplina, titulo, tipo, pagina, trecho in resultados:
        onde = f"página {pagina}" if tipo == "arquivo" else "anotação"
        st.markdown(f"**{titulo}** · {disciplina} · {onde}")
        st.markdown(trecho)