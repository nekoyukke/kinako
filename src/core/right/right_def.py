from dataclasses import dataclass
from enum import Enum

from src.core.source.source_span import SourceSpan

class Access(Enum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    def __repr__(self) -> str:
        return self.name

class Identity(Enum):
    NONE = "none"
    SHARED = "shared"
    UNIQUE = "unique"
    def __repr__(self) -> str:
        return self.name


@dataclass
class RightDef:
    access: Access
    identity: Identity
    span: SourceSpan
    def __repr__(self) -> str:
        return f"{self.access}, {self.identity}, {self.span}"