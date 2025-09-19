import requests
from .base import DomainBase
from .domain_info import DomainInfo, DomainStatus


class DomainPL(DomainBase):
    def __init__(self):
        super().__init__()

    def _loads(self, resp:requests.Response) -> DomainInfo:
        resp_status = resp.json().get("nask0_state")
        if resp_status == "registered":
            status = DomainStatus.REGISTERED
        elif resp_status == "available":
            status = DomainStatus.AVAILABLE
        else:
            status = DomainStatus.UNKNOWN
        return DomainInfo(
            domain=self._domain,
            status=status)






