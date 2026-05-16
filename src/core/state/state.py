from dataclasses import dataclass


@dataclass
class State:
    initialized: bool
    locked: bool