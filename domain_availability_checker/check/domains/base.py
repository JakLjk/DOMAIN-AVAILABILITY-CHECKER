from abc import ABC, abstractmethod
from typing import Self, Optional, Dict, Any
import requests

from .domain_info import DomainInfo, DomainStatus

class Domain(ABC):
    def __init__(self):
        self._domain:str = None
        self._RDAP_url:str = "https://rdap.org/{type}/{domain}"
        self._RDAP_type:str = "domain"
        self._RDAP_result:Optional[Dict[str, Any]] = None
        self._domain_info:Optional[DomainInfo] = None

    def __repr__(self):
        cls = self.__class__.__name__
        if self._domain_info:
            domain = self._domain_info.domain
            status = self._domain_info.status
        else:
            domain = None
            status = None
        return f"Class={cls} DomainInfo(domain={domain} status={status})"
    
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
        self.rdap_result = resp
        self._domain_info = self._loads(status)
        return self
    
    @property
    def rdap_result(self) -> Dict[str, Any]:
        if not self._RDAP_result:
            raise RuntimeError("RDAP result not set")
        return self._RDAP_result
    
    @rdap_result.setter
    def rdap_result(self, value:requests.Response):
        if value:
            self._RDAP_result = value.json()
        else:
            self._RDAP_result = None

    def _loads(
            self, 
            domain_status:DomainStatus) -> DomainInfo:
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
                domain=self._domain,
                status=self._status()
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

    def domain_info(self) -> DomainInfo:
        if not self._domain_info:
            raise RuntimeError("Domain info has to be rendered with the help of .get() method")
        return self._domain_info

    @abstractmethod
    def _status(self) -> DomainStatus:
        """
        Searches rdap result for status information 
        """
        raise NotImplementedError
    

