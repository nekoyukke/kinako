from dataclasses import dataclass

from src.core.contract.type.type import TypeDef, UserDefType, BuildinType
from src.core.contract.right.right import Right
from src.core.contract.policy.policy import Policy
from src.core.function.function import FunctionDef
from src.core.symbol.symbol import Var
from src.core.variable.variable import VariableDef

@dataclass(slots=True)
class Context:

    variables: dict[VariableDef]
    functions: dict[FunctionDef]
    typedefs: dict[UserDefType]
    buildin: dict[BuildinType]
    types: dict[TypeDef]

    right: dict[str, Right]
    policy: dict[str, Policy]
    buildin_type: dict[str, TypeDef]