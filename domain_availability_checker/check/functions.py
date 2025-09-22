import unicodedata


def domain_str(name:str, tld:str) -> str:
    tld = tld.replace(".", "")
    return name + "." + tld

def domain_tld(domain:str) -> str:
    return domain.strip().lower().split(".")[-1]

def remove_diactritics(text:str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(
        c for c in normalized
        if unicodedata.category(c) != "Mn"
    )

def domain_to_ascii(domain:str) -> str:
    return ".".join(remove_diactritics(label) for label in domain.lower().split(".") if label)

def domain_to_punycode(domain:str) -> str:
    return ".".join(label.encode("idna").decode("ascii") for label in domain.strip().lower().split(".") if label)


def domain_tld(domain:str) -> str:
    return domain.split(".")[-1]