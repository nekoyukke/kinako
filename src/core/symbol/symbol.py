from dataclasses import dataclass
from abc import ABC

from src.core.source.source_span import SourceSpan
from src.core.contract.contract import Contract
@dataclass(slots=True)
class Symbol(ABC):
    pass

@dataclass(slots=True)
class VariableSymbol(Symbol):
    name: str
    entity: Contract
    span: SourceSpan