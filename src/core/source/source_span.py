from dataclasses import dataclass

@dataclass(frozen=True)
class SourceSpan:
    line: int
    col: int
    len: int
    
    def __repr__(self) -> str:
        return f"Span({self.line},{self.col},{self.len})"