from src.frontend.parser.models.base import ASTNode, Contract, Parameter
import src.frontend.parser.models.expr as _expr
from dataclasses import dataclass


@dataclass(repr=False)
class Stmt(ASTNode):
    pass
# 宣言系
@dataclass(repr=False)
class VariableDeclStmt(Stmt):
    name: str
    contract: Contract
    left: _expr.Expr

@dataclass(repr=False)
class FunctionDeclStmt(Stmt):
    name: str
    result: Contract
    params: list[Parameter]

@dataclass(repr=False)
class ExprStmt(Stmt):
    expr: _expr.Expr

# ブロック系
@dataclass(repr=False)
class BlockStmt(Stmt):
    instr: list[Stmt]

@dataclass(repr=False)
class ProgramStmt(Stmt):
    instr: list[Stmt]

# 制御構文系
@dataclass(repr=False)
class Ifstmt(Stmt):
    cond: _expr.Expr
    then_stmt: Stmt
    else_stmt: Stmt | None

@dataclass(repr=False)
class WhileStmt(Stmt):
    cond: _expr.Expr
    loop: Stmt

@dataclass(repr=False)
class ForEachStmt(Stmt):
    iterator: _expr.Expr
    variable: _expr.Identifier
    contract: Contract
    loop: Stmt