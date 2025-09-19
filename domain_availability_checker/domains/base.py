from abc import ABC, abstractmethod
from typing import Self, Optional, Dict, Any
import requests

from .domain_info import DomainInfo, DomainStatus

class DomainBase(ABC):
    def __init__(self):
        self._domain:str = None
        self._RDAP_url:str = "https://rdap.org/{type}/{domain}"
        self._RDAP_type:str = "domain"
        self._RDAP_result:Optional[Dict[str, Any]] = None
        self._domain_info:Optional[DomainInfo] = None

    def __repr__(self):
        cls = self.__class__.__name__
        domain = self._domain or "-"
        return f"<ClassName {cls} domain={domain}>"
    
    def get(self, domain:str, timeout:float=10.0) -> Self:
        self._domain = domain
        url = self._RDAP_url.format(type=self._RDAP_type, domain=domain)
        try:
            resp = requests.get(url, timeout=timeout)
        except requests.RequestException as e:
            status = DomainStatus.ERROR
            self._domain_info = self._loads(status)
            return self
        status = self._initial_status(resp.status_code)
        self._domain_info = self._loads(status)
        return self
    
    def _loads(self, domain_status:DomainStatus) -> DomainInfo:
        """
        Loads detailed information about domain
        """
        if domain_status == DomainStatus.ERROR:
            return DomainInfo(
                domain=self._domain,
                status=domain_status,
            )
        if domain_status == DomainStatus.AVAILABLE:
            return DomainInfo(
                domain=self._domain,
                status=domain_status,
            )
        if domain_status == DomainStatus.UNKNOWN:
            return DomainInfo(
                domain=self._status,
            )
    
    @staticmethod
    def _initial_status(status_code:int) -> DomainStatus:
        """
        Loads initial information about domain status based on response status code
        """
        if status_code==404:
            return DomainStatus.AVAILABLE
        if status_code == 200:
            return DomainStatus.UNKNOWN
        if 500 <= status_code <= 600:
            return DomainStatus.ERROR
        return DomainStatus.UNKNOWN

    @property
    def domain_info(self) -> DomainInfo:
        if not self._domain_info:
            raise RuntimeError("Domain info has to be rendered with the help of .get() method")
        return self._domain_info
    
    def domain_status(self) -> DomainStatus:
        return self.domain_info.status

    @property
    @abstractmethod
    def _status(self) -> DomainStatus:
        raise NotImplementedError
    

