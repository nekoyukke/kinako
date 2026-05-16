from enum import Enum, auto
from dataclasses import dataclass

from src.core.id_base.symbol_id import SymbolId

class OwnershipKind(Enum):
    UNIQUE = auto()
    SHARED = auto()


@dataclass
class Owner:
    kind: OwnershipKind
    holder: SymbolId | None