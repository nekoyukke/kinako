from dataclasses import dataclass

from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.scope_id import ScopeId

@dataclass
class Scope():
    me: ScopeId
    symbols: dict[str, SymbolId]
    parent: ScopeId | None