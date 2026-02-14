from dataclasses import dataclass
from typing import Optional
@dataclass
class TypeObject():
    pass
@dataclass
class Type(TypeObject):
    bit:Optional[int]
    is_anysize:bool
@dataclass
class TypeInt(Type):
    is_sign:bool
@dataclass
class TypeString(TypeObject):
    pass
@dataclass
class TypeFloat(Type):
    pass
@dataclass
class TypeBool(TypeObject):
    pass
@dataclass
class TypeList(TypeObject):
    Generic:TypeObject
@dataclass
class TypeMut(TypeObject):
    Generic:TypeObject
@dataclass
class TypeBorrow(TypeObject):
    Generic:TypeObject
@dataclass
class TypePtr(TypeObject):
    Generic:TypeObject
@dataclass
class TypeArray(TypeObject):
    Generic:TypeObject
@dataclass
class TypeFunction(TypeObject):
    params:list[TypeObject]
    retype:TypeObject
@dataclass
class TypeNone(TypeObject):
    pass
@dataclass
class TypeAny(TypeObject):
    pass
@dataclass
class TypeDynamic(TypeObject):
    pass
