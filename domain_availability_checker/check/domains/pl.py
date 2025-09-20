import requests
from .base import Domain
from .domain_info import DomainInfo, DomainStatus


class DomainPL(Domain):
    def __init__(self):
        super().__init__()

    def _status(self):
        status = self.rdap_result.get("nask0_state")
        if status == "registered":
            return DomainStatus.REGISTERED
        elif status == "available":
            return DomainStatus.AVAILABLE
        else:
            return DomainStatus.UNKNOWN




