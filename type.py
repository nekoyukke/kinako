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
    @classmethod
    def _(cls):
        return TypeInt(None, False, False)

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
    len:int

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

@dataclass
class TypeTemplate(TypeObject):
    id:int
    # T1 T2 ,etc..

# function[arg=[T1,T2....], return=T0]
# call->function[arg=[T1,T2....], return=T0]
# arg->[T1,T2....]




