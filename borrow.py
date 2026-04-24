from myast import *
from dataclasses import dataclass
from enum import Enum


# 変数の状態
class BorrowState(Enum):
    UNINITIALIZED = 1 # まだ値が入っていない
    ACTIV = 2 # 値があり、自由に使用可能
    MOVED = 3 # 他へ移動済み。もう使えないぜ！
    BORROWED = 4 # 借用がある。変えないでね。
    BORROW = 5 # 借用してるぜ、俺は！
    def is_mutable(self) -> bool:
        match (self):
            case BorrowState.UNINITIALIZED:
                return True
            case BorrowState.ACTIV:
                return True
            case BorrowState.MOVED:
                return False
            case BorrowState.BORROW:
                return False
            case BorrowState.BORROWED:
                return False
            case _:
                return False

class ProjectionKind(Enum):
    FIELD = 0 # フィールドアクセス (.f)
    DEREF = 1 # 参照外し (*ptr)
    INDEX = 2 # 配列のインデックス ([i])

@dataclass(frozen=True)
class Projection:
    kind: ProjectionKind
    place: "Symbol | int | Place | None"

@dataclass(frozen=True)
class Place:
    local_id: Symbol
    projection: list[Projection] | None # どのフィールドか
    def is_prefix(self, base_proj: list[Projection] | None, target_proj: list[Projection] | None) -> bool:
        # 短い方のリストの長さ分だけ、中身が完全に一致するか
        base = base_proj or []
        target = target_proj or []
        if len(base) > len(target):
            return False
        for b, t in zip(base, target):
            if b != t:
                return False
        return True

    def places_conflict(self, p2: "Place") -> bool:
        if self.local_id != p2.local_id:
            return False
        # どちらかがどちらかの Prefix であれば、それは「同じメモリの道の上」にいる
        return self.is_prefix(self.projection, p2.projection) or self.is_prefix(p2.projection, self.projection)

# 変数自体に紐づけるやつ
# 参照はBorrwingCheckerに集約
@dataclass
class StaticBorrow():
    state: BorrowState

# Exprの結果の状態
class ResultState(Enum):
    OWNED = 1 # 俺の
    BORROWED = 2 # 誰かの

# Exprの結果
class ResultBorrow():
    result: ResultState
    have: Place | None
    state: BorrowState
