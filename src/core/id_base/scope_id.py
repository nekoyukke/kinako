from dataclasses import dataclass

@dataclass(frozen=True)
class ScopeId:
    value: int