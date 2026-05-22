from dataclasses import dataclass

from src.core.node.ast_base import ASTNode
from src.frontend.lexer.tokentype import TokenType
from src.core.id_base.symbol_id import SymbolId

@dataclass(repr=False)
class TypeNode(ASTNode):
    """型表記の基底"""
    pass


@dataclass(repr=False)
class PrimitiveTypeNode(TypeNode):
    """
    組み込み
    """
    # ここでトークン種別を再利用
    type_type: TokenType


@dataclass(repr=False)
class UserDefinedTypeNode(TypeNode):
    """
    自作クラス
    """
    name: str
    sym: SymbolId

@dataclass(repr=False)
class ArrayTypeNode(TypeNode):
    """
    あーりー
    """
    element_type: TypeNode
    size: int


@dataclass(repr=False)
class ListTypeNode(TypeNode):
    """
    りすと
    """
    element_type: TypeNode