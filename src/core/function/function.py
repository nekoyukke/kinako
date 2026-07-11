from dataclasses import dataclass

from src.core.context.id import TypeId, SymbolId
from src.core.ast.base import ASTNode
from src.core.source.source_span import SourceSpan

@dataclass
class FunctionDef:
    symbol: SymbolId

    parameters: list[TypeId]

    return_type: TypeId

    body: ASTNode

    span: SourceSpan