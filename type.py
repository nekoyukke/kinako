from dataclasses import dataclass
from typing import Any, Optional

MAXINTBIT = 128
MAXFLOATBIT = 128
MININTBIT = 8
MINFLOATBIT = 32

# 基底クラス
@dataclass
class TypeObject():
    def GetParents(self) -> list["TypeObject"]:
        return []
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
    @classmethod
    def _(cls):
        return TypeInt(None, False, False)
    # 先祖クラスを渡す
    def GetParents(self) -> list[TypeObject]:
        # AnyInt
        if self.is_anysize or self.bit is None:
            return [
                TypeFloat(MINFLOATBIT, is_anysize=False),
            ]
        # bit数が規定値を超えていたら
        if self.bit >= MAXINTBIT:
            return [
                TypeInt(None, True, True)
            ]
        # int num
        if self.is_sign:
            # int num*2
            return [
                TypeInt(bit=self.bit*2, is_anysize=False, is_sign=True),
            ]
        # uint num
        else:
            # uint num*2
            # int num
            return [
                TypeInt(bit=self.bit*2, is_anysize=False, is_sign=True),
                TypeInt(bit=self.bit, is_anysize=False, is_sign=False),
            ]


# string型
@dataclass
class TypeString(TipTypeObject):
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]

@dataclass
class TypeASCII(TypeString):
    def GetParents(self) -> list[TypeObject]:
        return [TypeString()] # ASCII は String の一種

@dataclass
class TypeUTF8(TypeString):
    def GetParents(self) -> list[TypeObject]:
        return [TypeString()] # UTF8 も String の一種

# float型
@dataclass
class TypeFloat(Type):
    @classmethod
    def _(cls):
        return TypeFloat(None, False)
    def GetParents(self) -> list[TypeObject]:
        if self.is_anysize or self.bit is None:
            return [
                TypeAny(),
            ]
        if self.bit < MAXFLOATBIT:
            return [
                TypeFloat(bit=self.bit*2, is_anysize=False),
            ]
        return [
            TypeFloat(bit=None,is_anysize=True)
        ]

# boolean型
@dataclass
class TypeBool(TipTypeObject):
    def GetParents(self) -> list[TypeObject]:
        return [
            TypeInt(MININTBIT, is_anysize=False, is_sign=False)
        ]

# None型
@dataclass
class TypeNone(TipTypeObject):
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]



# 特殊
# 任意型
@dataclass
class TypeAny(TypeObject):
    def GetParents(self) -> list[TypeObject]:
        return []

# 型推論型
@dataclass
class TypeDynamic(TypeObject):
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]

# テンプレート型
@dataclass
class TypeTemplate(TypeObject):
    id:int
    # SrcType DestType ,etc..
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]



# 肉
# うめぇ
@dataclass
class MiddleTypeObject(TypeObject):
    Generic:list[TypeObject]

# リスト型
@dataclass
class TypeList(MiddleTypeObject):
    Generic:list[TypeObject]
    def GetParents(self) -> list[TypeObject]:
        parents:list[TypeObject] = []
        for i, g in enumerate(self.Generic):
            for p in g.GetParents():
                new_generic = list(self.Generic)
                new_generic[i] = p
                parents.append(TypeList(Generic=new_generic))
        
        # 最後に Any へ合流
        parents.append(TypeAny())
        return parents

# ポインター型
@dataclass
class TypePtr(MiddleTypeObject):
    Generic:list[TypeObject]
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]

# 配列型
@dataclass
class TypeArray(MiddleTypeObject):
    Generic:list[TypeObject]
    len:int
    def GetParents(self) -> list[TypeObject]:
        return [TypeList(Generic=self.Generic),]

# 関数型
@dataclass
class TypeFunction(TypeObject):
    params:list[TypeObject]
    retype:TypeObject
    def GetParents(self) -> list[TypeObject]:
        return [TypeAny()]

# ユーザ型
@dataclass
class UserType(TypeObject):
    Name:str
    pearent:list[TypeObject]
    def GetParents(self) -> list[TypeObject]:
        return self.pearent
