from dataclasses import dataclass

from src.core.node.ast_base import ASTNode
from src.frontend.parser.models.expr import Expr, VariableNode
from src.frontend.parser.models.literal import StrLiteralNode
from src.frontend.parser.models.type import TypeNode
from src.core.possession.possession import Possession

@dataclass(repr=False)
class Stmt(ASTNode):
    pass


@dataclass(repr=False)
class LetStmt(Stmt):
    """
    変数
    """
    kind: Possession
    type: TypeNode
    name: VariableNode
    right: Expr | None


@dataclass(repr=False)
class ExprStmtNode(Stmt):
    """
    expr
    """
    expr: Expr


@dataclass(repr=False)
class BlockNode(Stmt):
    """
    blockたん
    """
    stmts: list[Stmt]


@dataclass(repr=False)
class IfStmtNode(Stmt):
    """
    condとか
    """
    cond: Expr
    then_stmt: Stmt
    else_stmt: Stmt | None


@dataclass(repr=False)
class WhileStmtNode(Stmt):
    cond: Expr
    body: Stmt


@dataclass(repr=False)
class ForStmtNode(Stmt):
    var: VariableNode
    expr: Expr
    body: Stmt


@dataclass(repr=False)
class FunctionDefineNode(Stmt):
    name: VariableNode
    body: Stmt
    args: list[VariableNode]
    arg_types: list[TypeNode]
    arg_Possession: list[Possession]
    return_type: TypeNode
    return_Possession: Possession


@dataclass(repr=False)
class ReturnStmtNode(Stmt):
    expr: Expr


@dataclass(repr=False)
class ImportNode(Stmt):
    From: StrLiteralNode


@dataclass(repr=False)
class Program(Stmt):
    blocks: list[Stmt]
    imports: list['Program']
    import_stmt: list[ImportNode]


@dataclass(repr=False)
class AnchorStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None


@dataclass(repr=False)
class GrabStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None


@dataclass(repr=False)
class HoldStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None

