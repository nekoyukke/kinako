from dataclasses import dataclass
from abc import ABC

from src.core.source.source_span import SourceSpan

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
    element: TypeDef

@dataclass
class ArrayType(BuildinType):
    element: TypeDef
    size: int

# 定義クラス
@dataclass
class UserDefType(TypeDef):
    member: list[TypeDef]
    span: SourceSpan