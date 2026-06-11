from dataclasses import dataclass
from enum import Enum

from src.frontend.parser.models.base import ASTNode


@dataclass(repr=False)
class Expr(ASTNode):
    pass

class BinaryKind(Enum):
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"

@dataclass(repr=False)
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

@dataclass(repr=False)
class UnaryExpr(Expr):
    expr: Expr
    op: UnaryKind

@dataclass(repr=False)
class Identifier(Expr):
    name:str
    generic: list[Identifier]

@dataclass(repr=False)
class CallExpr(Expr):
    call: Expr
    args: list[Expr]

class LogicKind(Enum):
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='

@dataclass(repr=False)
class LogicExpr(Expr):
    right: Expr
    left: Expr
    op: LogicKind

@dataclass(repr=False)
class Literal(Expr):
    pass

@dataclass(repr=False)
class BoolLiteral(Literal):
    is_true:bool

@dataclass(repr=False)
class IntLiteral(Literal):
    number:int

@dataclass(repr=False)
class FloatLiteral(Literal):
    number:float

@dataclass(repr=False)
class NoneLiteral(Literal):
    pass

@dataclass(repr=False)
class NullLiteral(Literal):
    pass

@dataclass(repr=False)
class StringLiteral(Literal):
    string:str