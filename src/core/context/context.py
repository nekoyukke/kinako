from dataclasses import dataclass
from typing import Any

from src.core.type.type_def import TypeDef
from src.core.right.right_def import RightDef
from src.core.policy.policy_def import PolicyDef
from src.core.function.function_def import FunctionDef
from src.core.alias.alias_def import TypeAliasDef, RightAliasDef, PolicyAliasDef
from src.core.symbol.symbol_def import Symbol


@dataclass
class Context():
    types: dict[str, TypeDef]
    rights: dict[str, RightDef]
    policies: dict[str, PolicyDef]
    # groups: dict[str, GroupDef]
    # interfaces: dict[str, InterfaceDef]
    functions: dict[str, FunctionDef]
    type_aliases: dict[str, TypeAliasDef]
    policy_aliases: dict[str, PolicyAliasDef]
    right_aliases: dict[str, RightAliasDef]
    # resolver
    resolved: dict[int, Symbol]

    def display(self, dictionary:dict[Any, Any]):
        string = ""
        if len(dictionary) == 0:
            return "\n    NONE"
        for k,v in dictionary.items():
            string += f"\n    {k}:{v}"
        return string

    def __repr__(self) -> str:
        string = "default"
        string += f"\ntype: {self.display(self.types)}"
        string += f"\nright: {self.display(self.rights)}"
        string += f"\npolicy: {self.display(self.policies)}"
        string += f"\nalias_type: {self.display(self.type_aliases)}"
        string += f"\nalias_right: {self.display(self.right_aliases)}"
        string += f"\nalias_policy: {self.display(self.policy_aliases)}"
        string += f"\n"
        string += f"\nfunction: {self.display(self.functions)}"
        string += f"\nresolved: {self.display(self.resolved)}"
        
        return string
