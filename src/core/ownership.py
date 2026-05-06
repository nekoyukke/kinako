from enum import IntFlag, auto

class Ownership(IntFlag):
    NONE = 0
    OWNED = auto() # 所有者
    WRITE = auto() # 書きこみOK
    READ = auto() # 読み込みOK
    BORROW = auto() # 参照であります
    FREEZE = auto() # 変更禁止
    SHARED = auto() # 複数