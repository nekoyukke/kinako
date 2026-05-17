
from src.core.symbol.symbol import Symbol
from src.core.type.type import Type
from src.core.possession.possession import Possession
from src.core.node.ast_base import ASTNode
from src.core.scope.scope import Scope

from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.scope_id import ScopeId
from src.core.id_base.type_id import TypeId
from src.core.id_base.possession_id import PossessionId
from src.core.id_base.node_id import NodeId

class CompilationContext:
    symbol_table: dict[SymbolId, Symbol]
    
    scope_table: dict[ScopeId, Scope]

    type_table: dict[TypeId, Type]

    possession_table: dict[PossessionId, Possession]

    node_table: dict[NodeId, ASTNode]