from dataclasses import dataclass

from src.core.context.id import ContextId, SymbolId

@dataclass(slots=True)
class Symbol:
    id: SymbolId
    name: str
    entity: ContextId