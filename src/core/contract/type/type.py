from dataclasses import dataclass
from abc import ABC

from src.core.source.source_span import SourceSpan

@dataclass
class TypeDef(ABC):
    pass

@dataclass
class BuildinType(TypeDef, ABC):
    pass

@dataclass
class UserDefType(TypeDef):
    member: list[TypeDef]
    span: SourceSpan