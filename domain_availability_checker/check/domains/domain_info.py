from dataclasses import dataclass
from enum import Enum, auto


class DomainStatus(Enum):
    REGISTERED= auto()
    AVAILABLE = auto()
    UNKNOWN = auto()
    ERROR = auto()
    THROTTLED = auto()

    def __str__(self):
        return self.name

@dataclass
class DomainInfo:
    domain:str
    status:DomainStatus