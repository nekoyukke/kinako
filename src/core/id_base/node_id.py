from dataclasses import dataclass

@dataclass(frozen=True)
class NodeId:
    value: int