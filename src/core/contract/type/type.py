from dataclasses import dataclass
from abc import ABC

from src.core.source.source_span import SourceSpan
from src.core.context.id import TypeId

@dataclass
class TypeDef(ABC):
    pass

# ビルドイン
@dataclass
class BuildinType(TypeDef, ABC):
    pass

@dataclass
class IntType(BuildinType):
    bit_size: int

@dataclass
class BooleanType(BuildinType):
    pass

@dataclass
class NoneType(BuildinType):
    pass

@dataclass
class PtrType(BuildinType):
    element: TypeId

@dataclass
class ArrayType(BuildinType):
    element: TypeId
    size: int

@dataclass
class UnionType(BuildinType):
    right: TypeId
    left: TypeId

# 定義クラス
@dataclass
class UserDefType(TypeDef):
    member: list[TypeId]
    span: SourceSpan