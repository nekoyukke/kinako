from dataclasses import dataclass

from src.core.source.source_span import SourceSpan

@dataclass
class Symbol:
    name: str
    span: SourceSpan
    def __repr__(self) -> str:
        return self.name