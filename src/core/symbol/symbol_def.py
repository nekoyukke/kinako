from dataclasses import dataclass

from src.core.type.type_def import TypeDef
from src.core.variable.variable_def import VariableDef

@dataclass
class Symbol:
    name: str
    def __repr__(self) -> str:
        return self.name

@dataclass
class TypeSymbol(Symbol):
    target: TypeDef
    def __repr__(self) -> str:
        return f"{self.name} ({self.target})"

@dataclass
class FunctionSymbol(Symbol):
    ref: str
    def __repr__(self) -> str:
        return f"{self.name} ({self.ref})"

@dataclass
class VariableSymbol(Symbol):
    target: VariableDef
    def __repr__(self) -> str:
        return f"{self.name} ({self.target})"