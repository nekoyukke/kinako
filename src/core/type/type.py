"""
純粋な型システム
"""

from dataclasses import dataclass


from src.core.id_base.symbol_id import SymbolId

@dataclass(frozen=True)
class Type():
    pass


@dataclass(frozen=True)
class LeafType(Type):
    pass


@dataclass(frozen=True)
class IntType(LeafType):
    bits: int
    sign: bool


@dataclass(frozen=True)
class FloatType(LeafType):
    bits: int


@dataclass(frozen=True)
class BoolType(LeafType):
    pass


@dataclass(frozen=True)
class UserType(LeafType):
    sym: SymbolId



@dataclass(frozen=True)
class GenericType(Type):
    def children(self) -> list[Type]:
        return []


@dataclass(frozen=True)
class ListType(GenericType):
    element: Type
    def children(self):
        return [self.element]


@dataclass(frozen=True)
class FunctionType(GenericType):
    args: list[Type]
    ret: Type
    def children(self):
        return [*self.args, self.ret]


@dataclass(frozen=True)
class ArrayType(GenericType):
    element: Type
    size: int
    def children(self):
        return [self.element]