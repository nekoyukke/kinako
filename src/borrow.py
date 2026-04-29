from dataclasses import dataclass
from enum import Enum

from src.myast import *
from src.utils import Error

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
    source: str
    map: dict[Place, StaticBorrow] = field(default_factory=dict[Place, StaticBorrow]) # 内部のシンボルと借り状況
    parent: Optional["BorrowScope"] = None # 親
    def deep(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.deep() + 1
    
    def get_parent(self):
        return self.parent
    
    def new_scope(self):
        return BorrowScope(self.source, {}, self)
    
    def cloce_scope(self):
        # 早期リターン
        if self.parent is None:
            return self
        
        for place, borrow in self.map.items():
            print(borrow)
            if not borrow.have is None:
                if borrow.state == BorrowState.BORROW:
                    self.map[borrow.have].release_borrow()
                    continue
                if borrow.vt == VariableType.BORROW:
                    self.map[borrow.have].release_borrow()
                    continue
                continue
            continue

        
        for place, borrow in self.map.items():
            free = borrow.get_free_borrow()
            if isinstance(free, Error):
                node = place.local_id.node
                raise AnalysisError(f"解放値に借用が入っています。{place.local_id.name},カウント数:{borrow.ref_count}", node.line, node.column, self.source, "", node.len)
            if free is None:
                # 正しい
                continue
            continue
        return self.parent

    def add_map(self, place:Place, borrow:StaticBorrow):
        self.map[place] = borrow

    def add_ref(self, place:Place):
        if not place in self.map:
            self.add_parent_place(place)
        self.map[place].add_borrow()
        return

    def add_state(self, place:Place, state:BorrowState):
        if not place in self.map:
            self.add_parent_place(place)
        self.map[place].state = state
        return
        
    def add_parent_place(self, place:Place):
        borrow = self.get_map(place)
        if borrow is None:
            raise
        self.map[place] = borrow
        return
    
    def del_map(self, place:Place):
        if not place in self.map:
            return
        self.map.pop(place)
    
    def get_map(self, place:Place) -> StaticBorrow | None:
        if place in self.map:
            return self.map[place]
        if place.projection:
            parent_place = Place(place.local_id, place.projection[:-1])
            parent_static = self.get_map(parent_place)
            return parent_static
        if self.parent is None:
            return None
        return self.parent.get_map(place)