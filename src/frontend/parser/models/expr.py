from dataclasses import dataclass
from enum import Enum

from src.frontend.parser.models.base import ASTNode
nr_dataclass = dataclass(repr=False)

@nr_dataclass
class Expr(ASTNode):
    pass

class BinaryKind(Enum):
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"

@nr_dataclass
class BinaryExpr(Expr):
    right: Expr
    left: Expr
    op: BinaryKind

class UnaryKind(Enum):
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"

@nr_dataclass
class UnaryExpr(Expr):
    expr: Expr
    op: UnaryKind

@nr_dataclass
class Identifier(Expr):
    name:str
    generic: list[Identifier]

@nr_dataclass
class CallExpr(Expr):
    call: Expr
    args: list[Expr]

class LogicKind(Enum):
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='

@nr_dataclass
class LogicExpr(Expr):
    right: Expr
    left: Expr
    op: LogicKind

@nr_dataclass
class Literal(Expr):
    pass

@nr_dataclass
class BoolLiteral(Literal):
    is_true:bool

@nr_dataclass
class IntLiteral(Literal):
    number:int

@nr_dataclass
class FloatLiteral(Literal):
    number:float

@nr_dataclass
class NoneLiteral(Literal):
    pass

@nr_dataclass
class NullLiteral(Literal):
    pass

@nr_dataclass
class StringLiteral(Literal):
    string:str