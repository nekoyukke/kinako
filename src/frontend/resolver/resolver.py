import difflib

from src.utils.error.resolver import KinakoResolverError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo, KinakoBaseError

from src.core.context.context import CompilationContext
from src.core.id_base.scope_id import ScopeId
from src.core.id_base.symbol_id import SymbolId

from src.core.node.ast_base import ASTNode
from src.frontend.parser.models import stmt
from src.frontend.parser.models import expr


# Symbolの取り付け

class Resolver:
    def __init__(self, program: stmt.Program, source:str, context:CompilationContext) -> None:
        self.program = program
        self.source = source
        self.context = context
        self.error: list[KinakoBaseError] = []
        return
    
    def call_error(self, message:str, node:ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoResolverError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
        raise err
    
    def resolve(self):
        self._visit_program()
        return
    
    def _visit_program(self):
        for s in self.program.blocks:
            self._visit_try_stmt(s)
    
    def _visit_try_stmt(self, node:stmt.Stmt):
        try:
            self._visit_stmt(node)
            return
        except KinakoResolverError:
            return
    
    def set_child(self, node:ASTNode):
        for i in node.get_child():
            if isinstance(i, expr.Expr):
                self._visit_expr(i)
                continue
            if isinstance(i, stmt.Stmt):
                self._visit_stmt(i)
                continue

    def _visit_stmt(self, node:stmt.Stmt):
        # 特殊処理
        if isinstance(node, stmt.BlockNode):
            for i in node.stmts:
                self._visit_try_stmt(i)
            return
        if isinstance(node, stmt.LetStmt):
            if node.right:
                self._visit_expr(node.right)
            return
        self.set_child(node)

    def get_symbol(self, name:str, scopeid:ScopeId) -> SymbolId | None:
        """
        理想的なシンボルを返す
        """
        if name in self.context.symbol.scope_table[scopeid].symbols:
            return self.context.symbol.scope_table[scopeid].symbols[name]
        parent = self.context.symbol.scope_table[scopeid].parent
        if parent: return self.get_symbol(name, parent)
        return None
    
    def get_names(self, name:str, scope:ScopeId, cc:int=1) -> list[str]:
        s = self.context.symbol.scope_table[scope]
        names:list[str] = []
        if s.parent:
            names += self.get_names(name, s.parent)
        names += list(s.symbols.keys())
        return difflib.get_close_matches(name, names, cc)

    def _visit_expr(self, node:expr.Expr):
        match (node):
            case expr.VariableNode():
                # セット
                if not node.scopeid:
                    self.call_error("スコープのidがないです。", node,)
                symid = self.get_symbol(node.name, node.scopeid)
                if symid:
                    self.context.expr.symbol_ref_table[node.id] = symid
                    return
                # もし複雑なエラーをする際には何か
                name = self.get_names(node.name, node.scopeid)
                if name:
                    help = KinakoHelp(f"'{name[0]}' ではありませんか？")
                    self.call_error(f"不明なシンボル名'{node.name}'", node, help=[help])
                self.call_error(f"不明なシンボル名'{node.name}'", node)
            case _:
                self.set_child(node)