from dataclasses import dataclass

from src.core.type.type_ref import TypeRef
from src.core.policy.policy_ref import PolicyRef
from src.core.right.right_ref import RightRef

@dataclass
class ParameterDef:
    name: str
    type: TypeRef
    policy: PolicyRef | None = None
    right: RightRef | None = None

@dataclass
class FunctionDef:
    name: str
    params: list[ParameterDef]
    return_type: TypeRef
    policy: PolicyRef | None = None
    right: RightRef | None = None