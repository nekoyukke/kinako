from dataclasses import dataclass
from typing import Generic

from src.core.abs_base import ASTNode, P, S
from src.frontend.models.expr import Expr, VariableNode
from src.frontend.models.literal import StrLiteralNode
from src.frontend.models.type import TypeNode
from src.core.owner.ownership import Ownership

@dataclass(repr=False)
class Stmt(ASTNode[S,P], Generic[S, P]):
    pass


@dataclass(repr=False)
class LetStmt(Stmt[S,P], Generic[S, P]):
    """
    変数
    """
    kind: Ownership
    type: TypeNode[S, P]
    name: VariableNode[S, P]
    right: Expr[S, P] | None


@dataclass(repr=False)
class ExprStmtNode(Stmt[S,P], Generic[S, P]):
    """
    expr
    """
    expr: Expr[S, P]


@dataclass(repr=False)
class BlockNode(Stmt[S,P], Generic[S, P]):
    """
    blockたん
    """
    stmts: list[Stmt[S, P]]


@dataclass(repr=False)
class IfStmtNode(Stmt[S,P], Generic[S, P]):
    """
    condとか
    """
    cond: Expr[S,P]
    then_stmt: Stmt[S,P]
    else_stmt: Stmt[S,P] | None


@dataclass(repr=False)
class WhileStmtNode(Stmt[S,P], Generic[S, P]):
    cond: Expr[S,P]
    body: Stmt[S,P]


@dataclass(repr=False)
class ForStmtNode(Stmt[S,P], Generic[S, P]):
    var: VariableNode[S,P]
    expr: Expr[S,P]
    body: Stmt[S,P]


@dataclass(repr=False)
class FunctionDefineNode(Stmt[S,P], Generic[S, P]):
    name: VariableNode[S,P]
    body: Stmt[S,P]
    args: list[VariableNode[S,P]]
    arg_types: list[TypeNode[S, P]]
    arg_Own: list[Ownership]
    return_type: TypeNode[S, P]
    return_Own: Ownership


@dataclass(repr=False)
class ReturnStmtNode(Stmt[S,P], Generic[S, P]):
    expr: Expr[S,P]


@dataclass(repr=False)
class ImportNode(Stmt[S,P], Generic[S, P]):
    From: StrLiteralNode[S,P]


@dataclass(repr=False)
class Program(Stmt[S,P], Generic[S, P]):
    blocks: list[Stmt[S,P]]
    imports: list['Program[S,P]']
    import_stmt: list[ImportNode[S,P]]


@dataclass(repr=False)
class AnchorStmtNode(Stmt[S,P], Generic[S,P]):
    variable: VariableNode[S,P]
    then_stmt: Stmt[S,P]
    else_stmt: Stmt[S,P] | None


@dataclass(repr=False)
class GrabStmtNode(Stmt[S,P], Generic[S,P]):
    variable: VariableNode[S,P]
    then_stmt: Stmt[S,P]
    else_stmt: Stmt[S,P] | None


@dataclass(repr=False)
class HoldStmtNode(Stmt[S,P], Generic[S,P]):
    variable: VariableNode[S,P]
    then_stmt: Stmt[S,P]
    else_stmt: Stmt[S,P] | None

