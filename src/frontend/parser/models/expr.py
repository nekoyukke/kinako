from dataclasses import dataclass
from typing import Generic
from enum import Enum, auto

from src.core.abs_base import ASTNode, P, S
from src.frontend.lexer.tokentype import TokenType
from src.frontend.parser.models.type import TypeNode
from src.core.value import ValueCategory

@dataclass(repr=False)
class Expr(ASTNode[S,P], Generic[S, P]):
    place: P | None
    category: ValueCategory


@dataclass(repr=False)
class BinaryOperationNode(Expr[S,P], Generic[S, P]):
    op: TokenType
    left: Expr[S,P]
    right: Expr[S,P]


@dataclass(repr=False)
class LogicalOperationNode(Expr[S,P], Generic[S, P]):
    op: TokenType
    left: Expr[S,P]
    right: Expr[S,P]


@dataclass(repr=False)
class UnaryOperationNode(Expr[S,P], Generic[S, P]):
    op: TokenType
    expr: Expr[S,P]


@dataclass(repr=False)
class AnchorNode(Expr[S,P], Generic[S, P]):
    expr: Expr[S,P]


@dataclass(repr=False)
class MoveNode(Expr[S,P], Generic[S, P]):
    expr: Expr[S,P]


@dataclass(repr=False)
class AssignNode(Expr[S,P], Generic[S, P]):
    op: TokenType
    left: Expr[S,P]
    right: Expr[S,P]


@dataclass(repr=False)
class CallNode(Expr[S,P], Generic[S, P]):
    func: Expr[S,P]
    args: list[Expr[S,P]]


@dataclass(repr=False)
class IndexAccessNode(Expr[S,P], Generic[S, P]):
    addr: Expr[S,P]
    index: Expr[S,P]


@dataclass(repr=False)
class AsCast(Expr[S,P], Generic[S, P]):
    expr: Expr[S, P]
    type: TypeNode[S, P]


@dataclass(repr=False)
class MemberAccessNode(Expr[S,P], Generic[S, P]):
    expr: Expr[S, P]
    right: str


class AccessModifier(Enum):
    NONE = auto()
    ANCHOR = auto() # @


@dataclass(repr=False)
class VariableNode(Expr[S,P], Generic[S,P]):
    """
    変数
    """
    name: str
    modifier: AccessModifier = AccessModifier.NONE
    Symbol: S | None = None