from dataclasses import dataclass
from typing import Generic, TypeVar

from src.core.abs_base import P, S
from frontend.parser.expr import Expr

T = TypeVar("T")


@dataclass
class LiteralNode(Expr[S,P], Generic[S,P,T]):
    """
    値を持つ
    """
    value: T


@dataclass
class IntLiteralNode(LiteralNode[S,P, int], Generic[S,P]):
    """
    整数
    """
    pass


@dataclass
class StrLiteralNode(LiteralNode[S,P, str], Generic[S,P]):
    """
    文字
    """
    pass


@dataclass
class FloatLiteralNode(LiteralNode[S,P, float], Generic[S,P]):
    """
    小数点
    """
    pass


@dataclass
class BoolLiteralNode(LiteralNode[S,P, bool], Generic[S,P]):
    """
    文字
    """
    pass
