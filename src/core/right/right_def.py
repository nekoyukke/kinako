from dataclasses import dataclass
from enum import Enum

class Access(Enum):
    Write = "write"
    Read = "read"

class Identity(Enum):
    Shared = "shared"
    Unique = "unique"

@dataclass
class RightDef:
    access: Access
    identity: Identity