from dataclasses import dataclass
from enum import Enum, auto


class DomainStatus(Enum):
    REGISTERED= auto()
    AVAILABLE = auto()
    UNKNOWN = auto()
    ERROR = auto()

@dataclass
class DomainInfo:
    domain:str
    status:DomainStatus