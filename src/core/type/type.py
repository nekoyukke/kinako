"""
純粋な型システム
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Type():
    pass


@dataclass(frozen=True)
class LeafType(Type):
    pass

@dataclass(frozen=True)
class GenericType(Type):
    def children(self) -> list[Type]:
        return []

