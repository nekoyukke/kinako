from dataclasses import dataclass

@dataclass(frozen=True)
class TypeId:
    value: int