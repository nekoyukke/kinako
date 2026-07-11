from dataclasses import dataclass
from enum import Enum
from abc import ABC

class AccessKind(Enum):
    NONE = 0
    READ = 1
    WRITE = 2

class IdentityKind(Enum):
    SHARED = 0
    UNIQUE = 1

@dataclass
class Right(ABC):
    pass

@dataclass
class RealRight(Right):
    access: AccessKind
    identity: IdentityKind

@dataclass
class Right_Union(Right):
    right: Right
    left: Right