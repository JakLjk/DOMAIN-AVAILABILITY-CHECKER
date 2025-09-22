from .functions import domain_tld
from .domains.base import Domain
from .domains.pl import DomainPL




DOMAIN_MAPPINGS = {
    "pl": DomainPL
}

def check_domain(domain:str) -> Domain:
    tld = domain_tld(domain)
    d = DOMAIN_MAPPINGS[tld]
    d = d()
    return d.get(domain)
