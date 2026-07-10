
from src.core.context.context import Context, ExprInfo
from src.core.identifier.identifier import Identifier, Variable

from src.core.core.type.type_def import TypeDef
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
