from dataclasses import dataclass
from abc import ABC

# Id

@dataclass(frozen=True, slots=True)
class ContextId(ABC):
    pass

@dataclass(frozen=True, slots=True)
class TypeId(ContextId):
    value: int

@dataclass(frozen=True, slots=True)
class SymbolId:
    value: int

@dataclass(frozen=True, slots=True)
class VariableId(ContextId):
    value: int

@dataclass(frozen=True, slots=True)
class FunctionId(ContextId):
    value: int