from dataclasses import dataclass
from enum import Enum, auto
from typing import Sequence

from src.core.abs_base import absSymbol, absProjection, absPlace


class ProjectionType(Enum):
    DOT = 0
    REF = auto()
    DREF = auto()
    INDEX = auto()


@dataclass(frozen=True)
class Projection(absProjection):
    """
    Placeの本実装
    """
    symbol: absSymbol
    type: ProjectionType

    @property
    def get_main(self) -> absSymbol:
        return self.symbol


class Place(absPlace):
    """
    Placeの実体。
    core.place.Place
    """

    def __init__(self, symbol:absSymbol, projection: list[Projection]) -> None:
        self.symbol: absSymbol = symbol
        self.projection: list[Projection] = projection

    @property
    def get_main(self) -> absSymbol:
        return self.symbol
    
    @property
    def get_projections(self) -> Sequence[Projection]:
        return self.projection

