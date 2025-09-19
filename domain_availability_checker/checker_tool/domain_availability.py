
import socket
import requests
from domains.pl import DomainPL


DOMAIN_MAPPINGS = {
    ".pl": DomainPL
}
    
def is_domain_available(domain:str):
    tld = domain.spl
    d = DomainPL().get(domain)
    print(d)
    return d.get_status

domain = "lejk.com"
print(is_domain_available(domain))