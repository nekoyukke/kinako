
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

from src.frontend.lexer.tokentype import TokenType

import src.core.type.type as ttype
import src.core.type.generic as tgeneric
import src.core.type.leaf as tleaf

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
                    self.ntype2type(node.type)
                case stmt.FunctionDefineNode():
                    pass
                case _:
                    self.call_error(f"不明な定義ノード。", node)

            self.context.symbol.type_table
    

    def ntype2type(self, ntyp:ntype.TypeNode) -> ttype.Type:
        match ntyp:
            case ntype.PrimitiveTypeNode():
                # non-generic
                return self.tok2type(ntyp)
            case ntype.ListTypeNode():
                return tgeneric.ListType(self.ntype2type(ntyp.element_type))
            case ntype.ArrayTypeNode():
                return tgeneric.ArrayType(self.ntype2type(ntyp.element_type), ntyp.size)
            case ntype.UserDefinedTypeNode():
                raise
            case _:
                self.call_error("不明なノード", ntyp)

    def tok2type(self, n:ntype.PrimitiveTypeNode) -> ttype.Type:
        match n.type_type:
            case TokenType.tINT8 | TokenType.tCHAR:
                return tleaf.IntType(8, True)
            case TokenType.tINT16 | TokenType.tSHORT:
                return tleaf.IntType(16, True)
            case TokenType.tINT32 | TokenType.tINT:
                return tleaf.IntType(32, True)
            case TokenType.tINT64 | TokenType.tLONG:
                return tleaf.IntType(64, True)
            case TokenType.tINT128:
                return tleaf.IntType(128, True)
            case TokenType.tUINT8:
                return tleaf.IntType(8, False)
            case TokenType.tUINT16:
                return tleaf.IntType(16, False)
            case TokenType.tUINT32:
                return tleaf.IntType(32, False)
            case TokenType.tUINT64:
                return tleaf.IntType(64, False)
            case TokenType.tUINT128:
                return tleaf.IntType(128, False)
            case TokenType.tFLOAT | TokenType.tFLOAT32:
                return tleaf.FloatType(32)
            case TokenType.tDOUBLE | TokenType.tFLOAT64:
                return tleaf.FloatType(64)
            case TokenType.tBOOL:
                return tleaf.BoolType()
            case TokenType.tAUTO:
                return tleaf.InferType()
            case TokenType.tANY:
                return tleaf.Any()
            case _:
                self.call_error(f"不明なリテラル'{n.type_type.name}'", n)
    
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