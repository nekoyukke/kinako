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
    def __repr__(self) -> str:
        if self.is_anysize or (self.bit is None):
            return f"Number"
        return f"{"U"*(not self.is_sign)}Int{self.bit}"

# string型
@dataclass
class TypeString(TipTypeObject):
    def __repr__(self) -> str:
        return "String"

@dataclass
class TypeASCII(TypeString):
    def __repr__(self) -> str:
        return "StringASCII"

@dataclass
class TypeUTF8(TypeString):
    def __repr__(self) -> str:
        return "StringUTF8"

# float型
@dataclass
class TypeFloat(Type):
    def __repr__(self) -> str:
        if self.is_anysize or (self.bit is None):
            return f"Number"
        return f"Float{self.bit}"

# boolean型
@dataclass
class TypeBool(TipTypeObject):
    def __repr__(self) -> str:
        return "Boolean"

# None型
@dataclass
class TypeNone(TipTypeObject):
    def __repr__(self) -> str:
        return "None"
# doing ぬるぽ
@dataclass
class TypeNull(TipTypeObject):
    def __repr__(self) -> str:
        return "Null"


# 特殊
# 任意型
@dataclass
class TypeAny(TypeObject):
    def __repr__(self) -> str:
        return "Any"

# 型推論型
@dataclass
class TypeDynamic(TypeObject):
    def __repr__(self) -> str:
        return "Dynamic"

# テンプレート型
@dataclass
class TypeTemplate(TypeObject):
    id:int
    # SrcType DestType ,etc..
    def __repr__(self) -> str:
        return f"Template{self.id}"



# 肉
# うめぇ
@dataclass
class MiddleTypeObject(TypeObject):
    pass

# リスト型
@dataclass
class TypeList(MiddleTypeObject):
    Generic:TypeObject
    def __repr__(self) -> str:
        return f"List<{self.Generic}>"
# ポインター型
@dataclass
class TypePtr(MiddleTypeObject):
    Generic:TypeObject
    def __repr__(self) -> str:
        return f"Ptr<{self.Generic}>"

# 配列型
@dataclass
class TypeArray(MiddleTypeObject):
    Generic:TypeObject
    len:int
    def __repr__(self) -> str:
        return f"Array<{self.Generic}, {self.len}>"

# まっぷ
@dataclass
class TypeMap(MiddleTypeObject):
    key:TypeObject
    value:TypeObject
    def __repr__(self) -> str:
        return f"Map<{self.key}, {self.value}>"

# 関数型
@dataclass
class TypeFunction(TypeObject):
    params:list[TypeObject]
    retype:TypeObject

@dataclass
class TypeBorrow(TypeObject):
    Generic:TypeObject

# ユーザ型
@dataclass
class UserType(TypeObject):
    Name:str

# Literal型
@dataclass
class LiteralType(TipTypeObject):
    def __repr__(self) -> str:
        return f"Literal"

# すうじ
@dataclass
class LiteralNumberType(LiteralType):
    def __repr__(self) -> str:
        return f"LiteralNumber"
# ふろーと
@dataclass
class LiteralDecimalType(LiteralType):
    def __repr__(self) -> str:
        return f"LiteralDecimal"
# もじ
@dataclass
class LiteralStringType(LiteralType):
    def __repr__(self) -> str:
        return f"LiteralString"
# りすと
@dataclass
class LiteralContainerType(LiteralType):
    Generic:TypeObject
    def __repr__(self) -> str:
        return f"LiteralContainer<{self.Generic}>"

Generic = (
    LiteralContainerType,
    TypeList,
    TypeArray,
    TypePtr,
    TypeBorrow
)