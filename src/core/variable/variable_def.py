from dataclasses import dataclass

from src.core.identifier.identifier import Identifier
from src.core.source.source_span import SourceSpan



@dataclass
class VariableDef:
    name: str
    span: SourceSpan
    type: Identifier | None = None
    policy: Identifier | None = None
    right: Identifier | None = None

    def __repr__(self) -> str:
        return f"{self.name}, {self.type}, {self.policy}, {self.right}, {self.span}"