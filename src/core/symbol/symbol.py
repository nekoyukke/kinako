from dataclasses import dataclass

from src.core.context.id import ContextId, SymbolId
from src.core.source.source_span import SourceSpan


@dataclass(slots=True)
class Symbol:
    id: SymbolId
    name: str
    entity: ContextId
    span: SourceSpan