from dataclasses import dataclass

@dataclass(frozen=True)
class SymbolId:
    value: int