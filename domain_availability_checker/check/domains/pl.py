from .base import Domain
from .domain_info import DomainInfo, DomainStatus



class DomainPL(Domain):
    def __init__(self):
        super().__init__()
        
    @property
    def whois_server(self) -> str:
        return "whois.dns.pl"
    
    def _status(self, response) ->DomainStatus:
        if "No information available" in response:
            return DomainStatus.AVAILABLE
        elif "DOMAIN NAME:" in response:
            return DomainStatus.REGISTERED
        else:
            return DomainStatus.UNKNOWN