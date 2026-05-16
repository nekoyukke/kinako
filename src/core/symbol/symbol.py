from __future__ import annotations

from dataclasses import dataclass


from src.core.abs_base import absType, ASTNode, absPlace, absSymbol
from src.core.id_base.symbol_id import SymbolId


@dataclass
class Symbol(absSymbol):
    """
    Symbol実体
    """
    fq_name: str
    name: str
    type: absType
    decl_node: 'ASTNode[Symbol, absPlace]'


    @property
    def get_fq_name(self) -> str: ...

    @property
    def get_name(self) -> str: ...

    @property
    def get_type(self) -> absType: ...

    @property
    def get_id(self) -> SymbolId: ...

    def get_decl_node(self) -> 'ASTNode[Symbol, absPlace]': ... 