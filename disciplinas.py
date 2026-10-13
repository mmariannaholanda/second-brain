#Salvar:
#Abrir o arquivo para escrita (se não existe, é criado).
#Para cada disciplina da lista, escrever o nome numa linha.
#Fechar o arquivo.

#Recuperar:
#Abrir o arquivo para leitura.
#Ler as linhas e montar uma lista.
#Fechar o arquivo.

disciplinas = ["Álgebra e Geometria", "Física", "FSC"] # lista da ram


# with open: abre o arquivo e garante que ele será fechado automaticamente quando você terminar de usar
#           nome do arq     write   a linguagem      cria a variavel
with open("disciplinas.txt", "w", encoding="utf-8") as arquivo:
    for nome in disciplinas:
        arquivo.write(nome + "\n")