from dataclasses import dataclass
from typing import Generic, TypeVar

from src.frontend.parser.models.expr import Expr

T = TypeVar("T")


@dataclass
class LiteralNode(Expr, Generic[T]):
    """
    値を持つ
    """
    value: T


@dataclass
class IntLiteralNode(LiteralNode[int]):
    """
    整数
    """
    pass


@dataclass
class StrLiteralNode(LiteralNode[str]):
    """
    文字
    """
    pass


@dataclass
class FloatLiteralNode(LiteralNode[float]):
    """
    小数点
    """
    pass


@dataclass
class BoolLiteralNode(LiteralNode[bool]):
    """
    文字
    """
    pass
