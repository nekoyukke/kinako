from dataclasses import dataclass

from src.core.type.type_ref import TypeRef
from src.core.right.right_ref import RightRef
from src.core.policy.policy_ref import PolicyRef

@dataclass
class TypeAliasDef:
    name: str
    target: TypeRef

@dataclass
class RightAliasDef:
    name: str
    target: list[RightRef]

@dataclass
class PolicyAliasDef:
    name: str
    target: PolicyRef