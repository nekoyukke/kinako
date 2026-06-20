from dataclasses import dataclass

from src.core.source.source_span import SourceSpan


@dataclass
class PolicyDef:
    name: str
    span: SourceSpan

    def __repr__(self) -> str:
        return f"{self.name}, {self.span}"