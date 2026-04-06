from dataclasses import dataclass
from typing import Optional

# 基底クラス
@dataclass
class TypeObject():
    pass
# 最先端クラス
@dataclass
class TipTypeObject(TypeObject):
    pass

@dataclass
class Type(TipTypeObject):
    bit:Optional[int] # bit = 2^n想定
    is_anysize:bool
    
# int型
@dataclass
class TypeInt(Type):
    is_sign:bool


# string型
@dataclass
class TypeString(TipTypeObject):
    pass

@dataclass
class TypeASCII(TypeString):
    pass

@dataclass
class TypeUTF8(TypeString):
    pass

# float型
@dataclass
class TypeFloat(Type):
    pass

# boolean型
@dataclass
class TypeBool(TipTypeObject):
    pass

# None型
@dataclass
class TypeNone(TipTypeObject):
    pass
# doing ぬるぽ
@dataclass
class TypeNull(TipTypeObject):
    pass


# 特殊
# 任意型
@dataclass
class TypeAny(TypeObject):
    pass

# 型推論型
@dataclass
class TypeDynamic(TypeObject):
    pass

# テンプレート型
@dataclass
class TypeTemplate(TypeObject):
    id:int
    # SrcType DestType ,etc..
    pass



# 肉
# うめぇ
@dataclass
class MiddleTypeObject(TypeObject):
    pass

# リスト型
@dataclass
class TypeList(MiddleTypeObject):
    Generic:TypeObject

# ポインター型
@dataclass
class TypePtr(MiddleTypeObject):
    Generic:list[TypeObject]

# 配列型
@dataclass
class TypeArray(MiddleTypeObject):
    Generic:TypeObject
    len:int

# 関数型
@dataclass
class TypeFunction(TypeObject):
    params:list[TypeObject]
    retype:TypeObject

# ユーザ型
@dataclass
class UserType(TypeObject):
    Name:str

# Literal型
@dataclass
class LiteralType(TipTypeObject):
    pass

# すうじ
@dataclass
class LiteralNumberType(LiteralType):
    pass
# ふろーと
@dataclass
class LiteralDecimalType(LiteralType):
    pass
# もじ
@dataclass
class LiteralStringType(LiteralType):
    pass