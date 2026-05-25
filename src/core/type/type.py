"""
純粋な型システム
"""

from dataclasses import dataclass
from enum import IntFlag, auto

class Operators(IntFlag):
    NONE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()

@dataclass(frozen=True)
class Type():
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class LeafType(Type):
    def get_can_Operators(self) -> Operators:
        return Operators.NONE

@dataclass(frozen=True)
class GenericType(Type):
    def children(self) -> list[Type]:
        return []
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class LiteralLeaf(LeafType):
    pass


@dataclass(frozen=True)
class NumberLeaf(LiteralLeaf):
    pass


@dataclass(frozen=True)
class FloatLeaf(LiteralLeaf):
    pass
