from src.frontend.parser.models.base import ASTNode, Contract, Parameter
import src.frontend.parser.models.expr as _expr
from dataclasses import dataclass
nr_dataclass = dataclass(repr=False)

@nr_dataclass
class Stmt(ASTNode):
    pass
# 宣言系
@nr_dataclass
class VariableDeclStmt(Stmt):
    name: str
    contract: Contract
    left: _expr.Expr

@nr_dataclass
class FunctionDeclStmt(Stmt):
    name: str
    result: Contract
    params: list[Parameter]

@nr_dataclass
class ExprStmt(Stmt):
    expr: _expr.Expr

# ブロック系
@nr_dataclass
class BlockStmt(Stmt):
    instr: list[Stmt]

@nr_dataclass
class ProgramStmt(Stmt):
    instr: list[Stmt]

# 制御構文系
@nr_dataclass
class Ifstmt(Stmt):
    cond: _expr.Expr
    then_stmt: Stmt
    else_stmt: Stmt

@nr_dataclass
class WhileStmt(Stmt):
    cond: _expr.Expr
    loop: Stmt

@nr_dataclass
class ForEachStmt(Stmt):
    iterator: _expr.Expr
    variable: _expr.Identifier
    contract: Contract
    loop: Stmt