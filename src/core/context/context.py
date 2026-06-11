from dataclasses import dataclass

from src.core.type.type_def import TypeDef
from src.core.right.right_def import RightDef
from src.core.policy.policy_def import PolicyDef
from src.core.function.function_def import FunctionDef
from src.core.alias.alias_def import TypeAliasDef, RightAliasDef, PolicyAliasDef

@dataclass
class Context():
    types: dict[str, TypeDef]
    rights: dict[str, RightDef]
    policys: dict[str, PolicyDef]
    # groups: dict[str, GroupDef]
    # interfaces: dict[str, InterfaceDef]
    functions: dict[str, FunctionDef]
    type_liases: dict[str, TypeAliasDef]
    policy_liases: dict[str, RightAliasDef]
    right_liases: dict[str, PolicyAliasDef]