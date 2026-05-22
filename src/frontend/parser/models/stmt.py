from __future__ import annotations

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
    
    def get_child(self) -> list[ASTNode]:
        if self.right:
            return [self.name, self.right]
        return [self.name,]


@dataclass(repr=False)
class ExprStmtNode(Stmt):
    """
    expr
    """
    expr: Expr

    def get_child(self) -> list[ASTNode]:
        return [self.expr]


@dataclass(repr=False)
class BlockNode(Stmt):
    """
    blockたん
    """
    stmts: list[Stmt]

    def get_child(self) -> list[ASTNode]:
        return [*self.stmts]


@dataclass(repr=False)
class IfStmtNode(Stmt):
    """
    condとか
    """
    cond: Expr
    then_stmt: Stmt
    else_stmt: Stmt | None

    def get_child(self) -> list[ASTNode]:
        if self.else_stmt:
            return [self.cond, self.then_stmt, self.else_stmt]
        return [self.cond, self.then_stmt]


@dataclass(repr=False)
class WhileStmtNode(Stmt):
    cond: Expr
    body: Stmt

    def get_child(self) -> list[ASTNode]:
        return [self.cond, self.body]


@dataclass(repr=False)
class ForStmtNode(Stmt):
    var: VariableNode
    expr: Expr
    body: Stmt
    def get_child(self) -> list[ASTNode]:
        return [self.var, self.expr, self.body]


@dataclass(repr=False)
class FunctionDefineNode(Stmt):
    name: VariableNode
    body: Stmt
    args: list[VariableNode]
    arg_types: list[TypeNode]
    arg_Possession: list[Possession]
    return_type: TypeNode
    return_Possession: Possession
    def get_child(self) -> list[ASTNode]:
        return [self.name, self.body, *self.args, *self.arg_types, self.return_type]


@dataclass(repr=False)
class ReturnStmtNode(Stmt):
    expr: Expr

    def get_child(self) -> list[ASTNode]:
        return [self.expr]


@dataclass(repr=False)
class ImportNode(Stmt):
    From: StrLiteralNode
    def get_child(self) -> list[ASTNode]:
        return [self.From]


@dataclass(repr=False)
class Program(Stmt):
    blocks: list[Stmt]
    imports: list['Program']
    import_stmt: list[ImportNode]
    
    def get_child(self) -> list[ASTNode]:
        return [*self.blocks, *self.imports, *self.import_stmt]


@dataclass(repr=False)
class AnchorStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None

    def get_child(self) -> list[ASTNode]:
        if self.else_stmt:
            return [self.variable, self.then_stmt, self.else_stmt]
        return [self.variable, self.then_stmt]


@dataclass(repr=False)
class GrabStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None

    def get_child(self) -> list[ASTNode]:
        if self.else_stmt:
            return [self.variable, self.then_stmt, self.else_stmt]
        return [self.variable, self.then_stmt]


@dataclass(repr=False)
class HoldStmtNode(Stmt):
    variable: VariableNode
    then_stmt: Stmt
    else_stmt: Stmt | None

    def get_child(self) -> list[ASTNode]:
        if self.else_stmt:
            return [self.variable, self.then_stmt, self.else_stmt]
        return [self.variable, self.then_stmt]

