
from src.core.symbol.symbol import Symbol
from src.core.type.type import Type
from src.core.possession.possession import Possession
from src.core.scope.scope import Scope
from src.core.state.state import State
from src.core.node.ast_base import ASTNode

from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.scope_id import ScopeId
from src.core.id_base.possession_id import PossessionId
from src.core.id_base.node_id import NodeId
from src.core.id_base.type_id import TypeId

class ExprStore:
    """
    変化するExprのみ。
    対象: type, nid2symbol, state,
    """
    type_table: dict[NodeId, Type] = {}
    symbol_ref_table: dict[NodeId, SymbolId] = {}
    state_table: dict[NodeId, State] = {}
    def __repr__(self) -> str:
        return f"table:\ntype:{self.type_table}\nref:{self.symbol_ref_table}\nstate:{self.state_table}"

class SymbolStore:
    """
    変化しないSymol系統
    対象:Scope, Symbol, Possession, Type, Decl_node
    """
    symbol_table: dict[SymbolId, Symbol] = {}
    decl_node: dict[SymbolId, ASTNode] = {}

    possession_table: dict[PossessionId, Possession] = {}
    scope_table: dict[ScopeId, Scope] = {}
    type_table: dict[TypeId, Type] = {}

    def __repr__(self) -> str:
        return f"table:\nsym:{self.symbol_table}\npos:{self.possession_table}\nscope:{self.scope_table}\ntype:{self.type_table}"

class CompilationContext:
    symbol: SymbolStore = SymbolStore()
    expr: ExprStore = ExprStore()

    def __repr__(self) -> str:
        return f"# static:\n{self.symbol.__repr__()}\n# dynamic:\n{self.expr.__repr__()}"