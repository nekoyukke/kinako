from dataclasses import dataclass

from src.core.identifier.identifier import Identifier as core_Identifier
from src.core.source.source_span import SourceSpan

@dataclass
class TypeAliasDef:
    name: str
    target: core_Identifier
    span: SourceSpan

@dataclass
class RightAliasDef:
    name: str
    target: list[core_Identifier]
    span: SourceSpan

@dataclass
class PolicyAliasDef:
    name: str
    target: core_Identifier
    span: SourceSpan