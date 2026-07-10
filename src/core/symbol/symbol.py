from dataclasses import dataclass
from enum import Enum, auto


class SymbolKind(Enum):
    VARIABLE = auto()
    FUNCTION = auto()
    TYPE = auto()


@dataclass(slots=True)
class Symbol:
    id: int
    name: str
    kind: SymbolKind
    entity: int