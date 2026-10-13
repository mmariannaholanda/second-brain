
#                          for read
with open("disciplinas.txt", "r", encoding="utf-8") as arquivo:
    for linha in arquivo:
        print(linha.strip()) # remove o quebra linha e n fica sempre com linha em branco
