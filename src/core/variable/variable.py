from dataclasses import dataclass

from src.core.source.source_span import SourceSpan
from 

@dataclass
class VariableDef:
    contract: Contract
    span: SourceSpan