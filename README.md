# Second Brain

Aplicativo pessoal para organizar a vida acadêmica e estudar com ajuda de IA.
Funciona no navegador, com dados guardados no próprio computador.

## O que ele faz

- Organiza o conteúdo em **semestres → disciplinas → arquivos e anotações**.
- Guarda **PDFs** (sem duplicatas, detectadas pelo hash do arquivo) e extrai o texto de cada página.
- Guarda **anotações** escritas por você.
- **Busca** palavras em todos os PDFs e anotações (SQLite FTS5).
- **Resume** PDFs e **mapeia os tópicos** usando o Gemini, só dos materiais que você marcar.
- **Gera prompts** de estudo para usar em outras IAs.
- Permite **mover** e **excluir** materiais, com confirmação.

## Privacidade

- Nada vai para a IA sem você marcar o material como "Disponível para IA" e clicar em resumir ou extrair.
- Anotações **nunca** são enviadas à IA.
- A chave da API fica no arquivo `.env`, que não vai para o GitHub.
- O banco (`secondbrain.db`) e os arquivos (`uploads/`) ficam só no seu computador e também não vão para o GitHub.

## Tecnologias

Python, Streamlit, SQLite, pypdf, Gemini (`google-genai`) e python-dotenv.

## Como rodar

Pré-requisitos: Python 3 e Git instalados.

1. Baixe o projeto e entre na pasta:
```
   git clone <endereço do repositório>
   cd second-brain
```
2. Crie e ative o ambiente virtual:
```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
```
   (no Linux ou Mac: `source .venv/bin/activate`)
3. Instale as dependências:
```
   pip install -r requirements.txt
```
4. Crie o arquivo `.env` copiando o `.env.example` e preencha com a sua chave do Gemini:
```
   GEMINI_API_KEY=sua_chave_aqui
   GEMINI_MODEL=gemini-3.8-flash
```
   O nome do modelo pode mudar com o tempo; confira os modelos disponíveis na sua conta.
5. Crie as tabelas do banco (só na primeira vez):
```
   python banco2.py
```
6. Abra o app:
```
   streamlit run app.py
```

Sem a chave do Gemini, tudo funciona, menos o resumo e o mapa de tópicos.

## Estrutura do projeto

| Arquivo ou pasta | Para que serve |
|---|---|
| `app.py` | A página inteira (interface e lógica) |
| `ia.py` | O único arquivo que fala com o Gemini; trocar de provedor mexe só aqui |
| `banco2.py` | Cria as tabelas do banco |
| `apoio/` | Scripts de apoio (ver dados, limpar testes) |
| `.streamlit/config.toml` | Cores e tema da página |
| `requirements.txt` | Lista das bibliotecas |
| `.env.example` | Modelo do `.env`, sem segredos |

## Limitações conhecidas

- O nome de uma disciplina só pode existir uma vez (mesmo em semestres diferentes).
- Os dados ficam em um banco local: não sincronizam entre computadores.
- PDFs escaneados (só imagem) não têm texto para indexar.
- Fórmulas extraídas de PDF podem vir com erros.
- Resumos e tópicos dependem de internet e dos limites gratuitos do Gemini.
- Uso individual: ainda não há contas de usuário nem compartilhamento.