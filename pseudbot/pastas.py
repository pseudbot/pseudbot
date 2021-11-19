# NOTE: Each pasta tweet should be no more than 263 characters long!


def get_pastas() -> list:
    pfile = open("pastas.txt", mode="r")
    pastas = pfile.read().split("\n\n")
    pfile.close()

    return pastas


PASTAS = get_pastas()


# TODO: make random picker only, rename
def concat_pasta(sep: str = " "):
    return sep.join([random.choice(PASTAS)])
