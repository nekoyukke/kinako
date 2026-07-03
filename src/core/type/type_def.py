from dataclasses import dataclass
from src.core.source.source_span import SourceSpan
from src.core.identifier.identifier import Identifier

@dataclass
class TypeDef:
    name: str
    span: SourceSpan
    def __repr__(self) -> str:
        return f"{self.name}, {self.span}"

@dataclass
class BuiltinTypeDef(TypeDef):
    pass

@dataclass
class FunctionTypeDef(TypeDef):
    parms: list[TypeDef]
    
    def __repr__(self) -> str:
        return f"({", ".join([i.__repr__() for i in self.parms])}), {self.span}"

@dataclass
class ClassTypeDef(TypeDef):
    fields: dict[str, Identifier]