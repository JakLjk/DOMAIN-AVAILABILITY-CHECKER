import socket

from abc import ABC, abstractmethod
from typing import Self, Optional, Literal

from .domain_info import DomainInfo, DomainStatus
from ..functions import domain_to_punycode, domain_tld, domain_to_ascii

class Domain(ABC):
    def __init__(self):
        self._domain:str = None
        self._domain_info:Optional[DomainInfo] = None   
        self._whois_response:str = None
        self._used_mode:str = None

    @property
    @abstractmethod
    def whois_server(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _status(self, response:str) -> DomainStatus:
        raise NotImplementedError

    def get(self, 
            domain:str,
            mode:Literal["ascii", "punycode"]="ascii") -> Self:
        self._domain = domain
        mode = mode.lower()
        self._used_mode = mode
        if mode == "ascii":
            domain_str = self.ascii_string
        elif mode == "punycode":
            domain_str = self.punycode_string
        else:
            raise ValueError(f"Incorrect mode: {mode}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.whois_server, 43))
                s.sendall((domain_str + "\r\n").encode("utf-8"))
                response = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    response += data
        self._whois_response = response.decode("utf-8", errors="ignore")
        status = self._status(self._whois_response )
        self._domain_info = self._loads(status)
        return self

    def _loads(self, domain_status:DomainStatus):
        return DomainInfo(
            domain=self.domain,
            status=domain_status)

    @property
    def domain(self):
        return self._domain
    
    @property
    def ascii_string(self):
        return domain_to_ascii(self.domain)
    
    @property
    def error_message(self):
        return ""
    
    @property
    def punycode_string(self):
        return domain_to_punycode(self.domain)
    
    @property
    def tld(self):
        return domain_tld(self.domain)
    
    @property
    def used_mode(self):
        return self._used_mode
    
    def domain_info(self) -> DomainInfo:
        if not self._domain_info:
            raise RuntimeError("Domain info has to be rendered with the help of .get() method")
        return self._domain_info



