

from src.utils.error.resolver import KinakoResolverError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo

from src.core.context.context import CompilationContext

from src.core.node.ast_base import ASTNode
from src.frontend.parser.models import stmt
from src.frontend.parser.models import expr


# Symbolの取り付け

class Resolver:
    def __init__(self, program: stmt.Program, source:str, context:CompilationContext) -> None:
        self.program = program
        self.source = source
        self.context = context
        self.error: list[KinakoResolverError] = []
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
    
    def _visit_stmt(self, node:stmt.Stmt):
        match (node):
            case stmt.LetStmt():
                if node.right:
                    self._visit_expr(node.right)
                return
            case _:
                self.call_error("不明なノード", node, help=[KinakoHelp(f"不明なノードです。{node.id}より。")])
                return
            

    def _visit_expr(self, node:expr.Expr):
        match (node):
            case expr.VariableNode():
                # セット
                node.name
                node.id
                self.context
                return
            case expr.BinaryOperationNode():
                self._visit_expr(node.left)
                self._visit_expr(node.right)
                return
            case _:
                return