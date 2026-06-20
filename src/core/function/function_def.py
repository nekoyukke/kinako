from dataclasses import dataclass

from src.core.identifier.identifier import Identifier
from src.core.source.source_span import SourceSpan


@dataclass
class ParameterDef:
    name: str
    span: SourceSpan
    type: Identifier | None = None
    policy: Identifier | None = None
    right: Identifier | None = None
    
    def __repr__(self) -> str:
        return f"{self.name}:({self.type}, {self.policy}, {self.right})"

@dataclass
class FunctionDef:
    name: str
    span: SourceSpan
    params: list[ParameterDef]
    return_type: Identifier | None = None
    policy: Identifier | None = None
    right: Identifier | None = None

    def __repr__(self) -> str:
        return f"{self.name} ({", ".join([i.__repr__() for i in self.params])})->({self.return_type}, {self.policy}, {self.right}) :: {self.span}"