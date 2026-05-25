from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.frontend.parser.models.expr import Expr


@dataclass
class LiteralNode(Expr):
    """
    値を持つ
    """
    value: Any


@dataclass
class IntLiteralNode(LiteralNode):
    """
    整数
    """
    value: int


@dataclass
class StrLiteralNode(LiteralNode):
    """
    文字
    """
    value: str


@dataclass
class FloatLiteralNode(LiteralNode):
    """
    小数点
    """
    value: float


@dataclass
class BoolLiteralNode(LiteralNode):
    """
    文字
    """
    value: bool
