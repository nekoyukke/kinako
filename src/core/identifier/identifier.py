from dataclasses import dataclass

@dataclass(repr=False)
class Variable():
    name:str
    def __repr__(self) -> str:
        return self.name

@dataclass(repr=False)
class Identifier():
    name:Variable
    generic: list[Identifier]

    def __repr__(self) -> str:
        if self.generic:
            return f"{self.name.__repr__()}[{", ".join([i.__repr__()for i in self.generic])}]"
        return self.name.__repr__()
