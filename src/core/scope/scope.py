from __future__ import annotations
from dataclasses import dataclass

from src.core.context.id import SymbolId

@dataclass(slots=True)
class Scope:
    parent: Scope | None
    symbols: dict[str, SymbolId]

    def get_variable(self) -> list[str]:
        if self.parent:
            return self.parent.get_variable()+list(self.symbols.keys())
        return list(self.symbols.keys())
    
    def check(self, name:str) -> bool:
        if self.parent:
            return self.parent.check(name)or (name in self.symbols)
        return (name in self.symbols)
    
    def lookup(self, name:str) -> SymbolId|None:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.lookup(name)
        return None