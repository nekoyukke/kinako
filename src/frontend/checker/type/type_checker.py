
from src.core.context.context import Context
from src.core.identifier.identifier import Identifier

from src.core.type.type_def import TypeDef
from src.core.symbol.symbol_def import Symbol, VariableSymbol


from src.utils.error.base import KinakoRelatedInfo, KinakoBaseError, KinakoHelp
from src.utils.error.type import KinakoTypeError

import src.frontend.parser.models.base as _base
import src.frontend.parser.models.stmt as _stmt
import src.frontend.parser.models.expr as _expr

"""
型処理。
ctx経由で型情報を取得し、当てはめる。
"""

class TypeChecker:
    def __init__(self, source:str, program:_stmt.ProgramStmt, ctx:Context) -> None:
        self.source = source
        self.program = program
        self.ctx = ctx
        self.error:list[KinakoBaseError] = []
        self.return_type:TypeDef
    
    def call_error(self, message:str, node:_base.ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoTypeError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)

    def check(self):
        for stmt in self.program.instr:
            self._visit_stmt(stmt)
        return
    
    def get_type(self, name:Identifier) -> TypeDef:
        # 名前から引く
        return self.ctx.types[name.name]

    def _get_node_id(self, ast: _base.ASTNode):
        return id(ast)

    def _visit_stmt(self, node:_stmt.Stmt) -> bool:
        match (node):
            case _stmt.VariableDeclStmt():
                right = node.contract.type
                if node.left is not None and right is not None:
                    left = self._visit_expr(node.left)
                    type = self.get_type(right.ident)
                    if left != type:
                        self.call_error("不明な型。", node)
                elif node.left is None and right is not None:
                    pass
                elif node.left is not None and right is None:
                    left = self._visit_expr(node.left)
                    sym:Symbol = self.ctx.resolved[self._get_node_id(node.name)]
                    if not isinstance(sym, VariableSymbol):
                        raise # おとしていいよん
                    sym.target.type = left
                else:
                    self.call_error("型推論ができませんでした。", node)
                return False
            case _:
                for i in node.get_child():
                    if isinstance(i, _stmt.Stmt):
                        self._visit_stmt(i)
                    elif isinstance(i, _expr.Expr):
                        self._visit_expr(i)
                return False

    def _visit_expr(self, node:_expr.Expr) -> TypeDef:
        match (node):
            case _:
                self.call_error("おい!kinakoが困ってるじゃないか!可愛がれよ!", node)
                raise