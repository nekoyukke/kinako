from dataclasses import dataclass
from enum import Enum
from copy import copy

from src.myast import *
from src.utils import Error, AnalysisError

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
    projection: tuple[Projection, ...] # どのフィールドか

    @classmethod
    def make(cls, sym:Symbol):
        return Place(sym, tuple())
    
    @classmethod
    def is_prefix(cls, base_proj: tuple[Projection, ...], target_proj: tuple[Projection, ...]) -> bool:
        # 短い方のリストの長さ分だけ、中身が完全に一致するか
        base = base_proj or []
        target = target_proj or []
        if len(base) > len(target):
            return False
        for b, t in zip(base, target):
            if b != t:
                return False
        return True

    def add_projection(self, projection:Projection):
        return Place(self.local_id, self.projection + (projection, ))

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
    vt: VariableType
    have: Place | None
    # 貸し出し数
    ref_count: int = 0

    def get_default_Borrow(self):
        match (self.vt):
            case VariableType.CONST :
                return BorrowState.ACTIV
            case VariableType.VAL:
                return BorrowState.ACTIV
            case VariableType.LET:
                return BorrowState.ACTIV
            case VariableType.MUT:
                return BorrowState.ACTIV
            case VariableType.BORROW:
                return BorrowState.BORROW
    
    def add_borrow(self):
        self.ref_count += 1
        self.state = BorrowState.BORROWED

    def release_borrow(self):
        self.ref_count -= 1
        if self.ref_count <= 0:
            self.ref_count = 0
            self.state = self.get_default_Borrow()

    # freeしたときのplace
    def get_free_borrow(self) -> Place | Error | None:
        if self.ref_count != 0:
            return Error()
        return self.have

# Exprの結果の状態
class ResultState(Enum):
    OWNED = 1 # 俺の
    BORROWED = 2 # 誰かの

# Exprの結果
@dataclass
class ResultBorrow():
    result: ResultState
    have: Place
    state: BorrowState

    def add_projection(self, projection:Projection):
        return ResultBorrow(self.result, self.have.add_projection(projection), self.state)
    


@dataclass
class BorrowScope:
    """
    親を汚さないような機構を採用
    基本的に自分のset/getはfree
    親のget/setはgetのみ。setは下のスコープからの伝播のみ。
    """
    source: str
    map: dict[Place, StaticBorrow] = field(default_factory=dict[Place, StaticBorrow]) # 内部のシンボルと借り状況
    parent: Optional["BorrowScope"] = None # 親
    
    # コピー！
    def clone(self):
        return BorrowScope(self.source, copy(self.map), self.parent)
    
    # 自分の環境から引いてくる
    def get_map_me(self, place:Place):
        return self.map.get(place)
    
    # 自分の環境にセット
    def set_map_me(self, place:Place, static:StaticBorrow):
        self.map[place] = static
        return

    # 自分以上の環境からの取得
    def get_map(self, place:Place) -> StaticBorrow | None:
        result = self.get_map_me(place)
        parent = self.get_parent()
        if result is None:
            if parent is None: return None
            return parent.get_map(place)
        return result
    
    # 親の環境から自分の環境にコピー
    def set_map_2me(self, place:Place):
        static = self.get_map(place)
        if static is None: return
        self.map[place] = static

    # 親を取得
    def get_parent(self):
        return self.parent

    # 指定のplaceの伝播
    def propagate_2parent(self, place:Place, node:Stmt|Expr):
        static = self.get_map_me(place)
        if static is None: return
        parent = self.get_parent()
        if parent is None: return
        parent_static = parent.get_map_me(place)
        if static.ref_count != 0:
            # ただし例外
            if parent_static is None:
                raise AnalysisError(f"借用中の値'{place}'はスコープを閉じれません。", node.line, node.column, self.source, "", node.len)
            if parent_static.ref_count != static.ref_count:
                raise AnalysisError(f"借用中の値'{place}'はスコープを閉じれません。", node.line, node.column, self.source, "", node.len)
            pass
        if parent_static is None: return
        parent.set_map_me(place, static)
        return
    
    # すべて伝播
    def close_scope(self, node:Stmt|Expr):
        for p, static in self.map.items():
            have = static.have
            if have is None: continue
            p = self.get_map(have)
            if p is None: continue
            p.release_borrow()
        
        for p, static in self.map.items():
            self.propagate_2parent(p, node)