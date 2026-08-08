from dataclasses import dataclass
from abc import ABC

@dataclass
class Policy(ABC):
    pass

@dataclass
class Policy_Union(Policy):
    right: Policy
    left: Policy

@dataclass
class Policy_Generic(Policy):
    element: Policy
    out: Policy

@dataclass
class Mutex(Policy):
    pass

@dataclass
class Arc(Policy):
    pass