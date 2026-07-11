from dataclasses import dataclass

from src.core.contract.type.type import TypeDef, UserDefType
from src.core.contract.right.right import Right
from src.core.contract.policy.policy import Policy
from src.core.function.function import FunctionDef
from src.core.symbol.symbol import Symbol
from src.core.variable.variable import VariableDef

@dataclass(slots=True)
class Context:
    symbols: list[Symbol]

    variables: list[VariableDef]
    functions: list[FunctionDef]
    typedefs: list[UserDefType]

    types: list[TypeDef]
    right: dict[str, Right]
    policy: dict[str, Policy]