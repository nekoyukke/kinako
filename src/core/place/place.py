from dataclasses import dataclass
from enum import Enum, auto

from src.core.symbol.symbol import Symbol

class ProjectionKind(Enum):
    DOT = 0
    REF = auto()
    DREF = auto()
    INDEX = auto()


@dataclass(frozen=True)
class Projection():
    """
    Placeの本実装
    """
    symbol: Symbol
    kind: ProjectionKind

@dataclass
class Place():
    """
    Placeの実体。
    core.place.Place
    """

    symbol: Symbol
    projection: list[Projection]