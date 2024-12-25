import random

nomes = ["Ana", "Carlos", "Mariana", "João", "Fernanda", "Pedro", "Luísa", "Lucas"]


random.shuffle(nomes)


grupo1 = nomes[:4]
grupo2 = nomes[4:]


print("Grupo 1:", grupo1)
print("Grupo 2:", grupo2)
