from dataclasses import dataclass
from enum import Enum, auto

from src.core.node.ast_base import ASTNode
from src.frontend.lexer.tokentype import TokenType
from src.frontend.parser.models.type import TypeNode

from src.core.place.place import Place

@dataclass(repr=False)
class Expr(ASTNode):
    place: Place | None


@dataclass(repr=False)
class BinaryOperationNode(Expr):
    op: TokenType
    left: Expr
    right: Expr
    
    def get_child(self) -> list[ASTNode]:
        return [self.left, self.right]


@dataclass(repr=False)
class LogicalOperationNode(Expr):
    op: TokenType
    left: Expr
    right: Expr

    def get_child(self) -> list[ASTNode]:
        return [self.left, self.right]


@dataclass(repr=False)
class UnaryOperationNode(Expr):
    op: TokenType
    expr: Expr
    def get_child(self) -> list[ASTNode]:
        return [self.expr]


@dataclass(repr=False)
class MoveNode(Expr):
    expr: Expr

    def get_child(self) -> list[ASTNode]:
        return [self.expr]


@dataclass(repr=False)
class AssignNode(Expr):
    op: TokenType
    left: Expr
    right: Expr
    def get_child(self) -> list[ASTNode]:
        return [self.left, self.right]


@dataclass(repr=False)
class CallNode(Expr):
    func: Expr
    args: list[Expr]

    def get_child(self) -> list[ASTNode]:
        return [self.func, *self.args]


@dataclass(repr=False)
class IndexAccessNode(Expr):
    addr: Expr
    index: Expr
    
    def get_child(self) -> list[ASTNode]:
        return [self.addr, self.index]


@dataclass(repr=False)
class AsCast(Expr):
    expr: Expr
    type: TypeNode

    def get_child(self) -> list[ASTNode]:
        return [self.expr, self.type]


@dataclass(repr=False)
class MemberAccessNode(Expr):
    expr: Expr
    right: VariableNode

    def get_child(self) -> list[ASTNode]:
        return [self.expr, self.right]


class AccessModifier(Enum):
    NONE = auto()
    ANCHOR = auto() # @


@dataclass(repr=False)
class VariableNode(Expr):
    """
    変数
    """
    name: str
    modifier: AccessModifier = AccessModifier.NONE