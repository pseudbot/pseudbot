# NOTE: Each pasta tweet should be no more than 263 characters long!


def get_pastas() -> list:
    pfile = open("pastas.txt", mode="r")
    pastas = pfile.read().split("\n\n")
    pfile.close()

    for n in range(len(pastas)):
        pastas[n] = pastas[n].split("\n")

    return pastas


PASTAS = get_pastas()
