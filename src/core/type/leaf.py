from dataclasses import dataclass

from src.core.id_base.symbol_id import SymbolId

from src.core.type.type import LeafType

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
class Any(LeafType):
    pass


@dataclass(frozen=True)
class InferType(LeafType):
    pass