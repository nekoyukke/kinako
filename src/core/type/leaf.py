from dataclasses import dataclass

from src.core.id_base.symbol_id import SymbolId

from src.core.type.type import LeafType, Operators

@dataclass(frozen=True)
class IntType(LeafType):
    bits: int
    sign: bool
    def get_can_Operators(self) -> Operators:
        return Operators.ADD | Operators.SUB | Operators.MUL | Operators.DIV | Operators.MOD


@dataclass(frozen=True)
class FloatType(LeafType):
    bits: int
    def get_can_Operators(self) -> Operators:
        return Operators.ADD | Operators.SUB | Operators.MUL | Operators.DIV

@dataclass(frozen=True)
class BoolType(LeafType):
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class UserType(LeafType):
    sym: SymbolId
    def get_can_Operators(self) -> Operators:
        return Operators.NONE

@dataclass(frozen=True)
class Any(LeafType):
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class InferType(LeafType):
    def get_can_Operators(self) -> Operators:
        return Operators.NONE
