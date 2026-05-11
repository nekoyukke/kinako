from __future__ import annotations

from dataclasses import dataclass


from src.core.abs_base import absType, ASTNode, absPlace, absSymbol

@dataclass
class Symbol(absSymbol):
    """
    Symbol実体
    """
    @property
    def get_fq_name(self) -> str: ...

    @property
    def get_name(self) -> str: ...

    @property
    def get_type(self) -> absType: ...

    def get_decl_node(self) -> 'ASTNode[Symbol, absPlace]': ... 