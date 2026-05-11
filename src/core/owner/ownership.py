from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag, auto

class OwnershipFlag(IntFlag):
    NONE = 0

    COPYABLE = auto() # コピーOK
    MOVABLE = auto() # 移動OK
    MUTABLE = auto() # 変更OK
    
    SENDABLE = auto() # スレッドsendOK
    THREADSAFE = auto() # スレッドセーフか
    
    BORROWABLE = auto() # 借用OK
    SHAREDBORROW = auto() # 複数不変借用
    EXCLUSIVEBORROW = auto() # 排他的な借用
    
    ATOMICACCESS = auto() # 原子サポート
    NOALIAS = auto() # 別名禁止


@dataclass
class Ownership():
    flag: OwnershipFlag
    generic: Ownership | None