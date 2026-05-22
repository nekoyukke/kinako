
from src.utils.error.type import KinakoTypeError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo, KinakoBaseError

from src.core.context.context import CompilationContext
from src.core.id_base.scope_id import ScopeId
from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.type_id import TypeId

from src.core.node.ast_base import ASTNode
from src.frontend.parser.models import stmt
from src.frontend.parser.models import expr
import src.frontend.parser.models.type as ntype

class TypeChecker():
    def __init__(self, program: stmt.Program, source:str, context:CompilationContext) -> None:
        self.program = program
        self.source = source
        self.context = context
        self.error: list[KinakoBaseError] = []
        self.type_id:int = 0
        return
    
    def call_error(self, message:str, node:ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoTypeError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
        raise err
    
    def check_type(self):
        self.decl_set_type()
        self._visit_program()
        return
    
    def male_type(self):
        res = TypeId(self.type_id)
        self.type_id += 1
        return res
    
    def decl_set_type(self):
        # 事前のセット
        sym_table = list(self.context.symbol.symbol_table.keys())
        for symid in sym_table:
            node = self.context.symbol.decl_node[symid]
            sym = self.context.symbol.symbol_table[symid]
            match node:
                case stmt.LetStmt():
                    node.type
                case stmt.FunctionDefineNode():
                    pass
                case _:
                    self.call_error(f"不明な定義ノード。", node)

            self.context.symbol.type_table
    

    def ntype2type(self, ntyp:ntype.TypeNode):
        

    
    def _visit_program(self):
        for s in self.program.blocks:
            self._visit_try_stmt(s)
    
    def _visit_try_stmt(self, node:stmt.Stmt):
        try:
            self._visit_stmt(node)
            return
        except KinakoTypeError:
            return

    def _visit_stmt(self, node:stmt.Stmt):
        if isinstance(node, stmt.BlockNode):
            for i in node.stmts:
                self._visit_try_stmt(i)
            return
        if isinstance(node, stmt.LetStmt):
            if node.right:
                self._visit_check(node.right)
            return
        self._visit_check(node)
    
    def _visit_check(self, node:ASTNode):
        for i in node.get_child():
            match i:
                case expr.Expr():
                    self._visit_expr(i)
                case _:
                    continue
    
    def _visit_expr(self, node:expr.Expr):
        pass