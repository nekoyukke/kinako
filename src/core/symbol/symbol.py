from __future__ import annotations

from dataclasses import dataclass


from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.type_id import TypeId
from src.core.id_base.possession_id import PossessionId
from src.core.id_base.scope_id import ScopeId
from src.core.id_base.node_id import NodeId

@dataclass(kw_only=True)
class Symbol():
    """
    Symbol実体
    """
    id: SymbolId
    fq_name: str
    name: str

    decl_node: NodeId
    possession_id: PossessionId
    type_id: TypeId | None = None
    scope_id: ScopeId