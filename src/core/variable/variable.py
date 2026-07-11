from dataclasses import dataclass
from src.core.contract.policy.policy import Policy
from src.core.contract.right.right import Right

from src.core.context.id import SymbolId, TypeId
from src.core.source.source_span import SourceSpan

@dataclass
class VariableDef:
    symbol: SymbolId

    type: TypeId

    right: Right

    policy: Policy
    span: SourceSpan