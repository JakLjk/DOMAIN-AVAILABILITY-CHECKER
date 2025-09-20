
def domain_str(name:str, tld:str) -> str:
    tld = tld.replace(".", "")
    return name + "." + tld

def domain_tld(domain:str) -> str:
    return domain.strip().lower().split(".")[-1]


def domain_to_punycode(domain:str) -> str:
    return ".".join(label.encode("idna").decode("ascii") for label in domain.strip().lower().split(".") if label)


def domain_tld(domain:str) -> str:
    return domain.split(".")[-1]