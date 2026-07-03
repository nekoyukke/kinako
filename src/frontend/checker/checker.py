
from src.core.context.context import Context, ExprInfo
from src.core.identifier.identifier import Identifier, Variable

from src.core.type.type_def import TypeDef
from src.core.symbol.symbol_def import Symbol


from src.utils.error.base import KinakoRelatedInfo, KinakoBaseError, KinakoHelp
from src.utils.error.type import KinakoTypeError

import src.frontend.parser.models.base as _base
import src.frontend.parser.models.stmt as _stmt
import src.frontend.parser.models.expr as _expr

"""
型/権利処理。
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
    
    def get_type(self, name:Variable) -> TypeDef:
        # 名前から引く
        return self.ctx.types[name.name]
    
    def _get_node_id(self, ast: _base.ASTNode):
        return id(ast)
    
    def _get_type(self, sym:Symbol) -> ExprInfo | None:
        return self.ctx.checker[sym]

    def _visit_stmt(self, node:_stmt.Stmt) -> bool:
        match (node):
            case _stmt.VariableDeclStmt():
                right = node.contract.type
                sym = self.ctx.resolved[self._get_node_id(node.name)]
                # rightとleftをもとにそれぞれがnoneの可能性でいろいろしてる
                if node.left is not None and right is not None:
                    # どっちも実体ある
                    left = self._visit_expr(node.left).type
                    type = self.get_type(right.name)
                    if left != type:
                        self.call_error("不明な型。", node)
                    else:
                        self.ctx.checker[node] = ExprInfo(left, right)
                elif node.left is None and right is not None:
                    self.ctx.checker[sym] = ExprInfo(self.get_type(right.name), right) # ここをget_rightに委託。 get_rightはif nonrならデフォルト（read+unique）を返す
                elif node.left is not None and right is None:
                    left = self._visit_expr(node.left)
                    sym:Symbol = self.ctx.resolved[self._get_node_id(node.name)]
                    self.ctx.checker[sym] = left
                else:
                    self.call_error("型推論ができませんでした。", node)
                return False
            case _stmt.Ifstmt():
                cond = self._visit_expr(node.cond).type
                if cond != self.ctx.types["bool"]:
                    self.call_error(f"条件部分はboolean型でなければなりません。実際の型{cond}", node)
                then_ret = self._visit_stmt(node.then_stmt)
                else_ret = False

                if node.else_stmt:
                    else_ret = self._visit_stmt(node.else_stmt)

                # ifの両側で落ちている必要があるぜ
                return then_ret and else_ret
            case _:
                isret = False
                for i in node.get_child():
                    if isinstance(i, _stmt.Stmt):
                        isret = isret or self._visit_stmt(i)
                    elif isinstance(i, _expr.Expr):
                        self._visit_expr(i)
                return isret

    def _visit_expr(self, node:_expr.Expr) -> ExprInfo:
        match (node):
            case _expr.Variable():
                node.ident.name
                sym = self.ctx.resolved[self._get_node_id(node)]
                return
            case _:
                self.call_error("おい!kinakoが困ってるじゃないか!可愛がれよ!", node)
                raise