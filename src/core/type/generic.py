from dataclasses import dataclass

from src.core.type.type import GenericType, Type, Operators


@dataclass(frozen=True)
class ListType(GenericType):
    element: Type
    def children(self):
        return [self.element]
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class FunctionType(GenericType):
    args: list[Type]
    ret: Type
    def children(self):
        return [*self.args, self.ret]
    def get_can_Operators(self) -> Operators:
        return Operators.NONE


@dataclass(frozen=True)
class ArrayType(GenericType):
    element: Type
    size: int
    def children(self):
        return [self.element]
    def get_can_Operators(self) -> Operators:
        return Operators.NONE