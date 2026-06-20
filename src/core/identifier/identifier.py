from dataclasses import dataclass

@dataclass(repr=False)
class Identifier():
    name:str
    generic: list[Identifier]

    def __repr__(self) -> str:
        if self.generic:
            return f"{self.name}[{", ".join([i.__repr__()for i in self.generic])}]"
        return self.name
