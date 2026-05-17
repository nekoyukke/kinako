from dataclasses import dataclass

@dataclass(frozen=True)
class ScopeId:
    value: int

    
    def __str__(self) -> str:
        return f"scope_{self.value}"