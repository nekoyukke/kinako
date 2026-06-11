from dataclasses import dataclass
from src.core.type.type_ref import TypeRef

@dataclass
class TypeDef:
    name: str

@dataclass
class BuiltinTypeDef(TypeDef):
    pass

@dataclass
class ClassTypeDef(TypeDef):
    fields: dict[str, TypeRef]