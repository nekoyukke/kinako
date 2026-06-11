from dataclasses import dataclass



@dataclass
class Context():
    types: dict[str, Type]
    rights: dict[str, Right]
    policys: dict[str, Policy]
    # groups: dict[str, Group]
    # interfaces: dict[str, Interface]
    functions: dict[str, Function]
    type_liases: dict[str, Aliasses]
    policy_liases: dict[str, Aliasses]
    right_liases: dict[str, Aliasses]