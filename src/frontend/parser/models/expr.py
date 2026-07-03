from dataclasses import dataclass
from enum import Enum

from src.frontend.parser.models.base import ASTNode
from src.core.identifier.identifier import Variable as core_Variable

@dataclass(repr=False)
class Expr(ASTNode):
    pass

class BinaryKind(Enum):
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"
    LOGIC_OR = "||"
    LOGIC_AND = "&&"

@dataclass(repr=False)
class BinaryExpr(Expr):
    left: Expr
    right: Expr
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
class Variable(Expr):
    ident: core_Variable

@dataclass(repr=False)
class CallExpr(Expr):
    call: Expr
    args: list[Expr]

class LogicKind(Enum):
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='
    GT = ">"
    LT = "<"

@dataclass(repr=False)
class LogicExpr(Expr):
    left: Expr
    right: Expr
    op: LogicKind

class AssignKind(Enum):
    ASSIGN = r'='
    PULS = r'+='
    MINUS = r'-='
    MULT = r'*='
    DIV = r'/='

@dataclass(repr=False)
class AssignExpr(Expr):
    left: Expr
    right: Expr
    op: AssignKind

@dataclass(repr=False)
class AccessExpr(Expr):
    pass

@dataclass(repr=False)
class IndexExpr(AccessExpr):
    expr: Expr
    index: Expr

@dataclass(repr=False)
class MemberExpr(AccessExpr):
    expr: Expr
    member: Variable


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


kinds = LogicKind | UnaryKind | AssignKind | BinaryKind