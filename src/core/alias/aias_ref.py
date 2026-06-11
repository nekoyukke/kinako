from dataclasses import dataclass

@dataclass
class TypeAliasRef:
    name: str

@dataclass
class RightAliasRef:
    name: str

@dataclass
class PolicyAliasRef:
    name: str