from dataclasses import dataclass

from src.core.type.type import GenericType, Type


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