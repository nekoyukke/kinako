from dataclasses import dataclass
from typing import Generic

from src.core.abs_base import ASTNode, P, S
from src.frontend.models.tokentype import TokenType


@dataclass(repr=False)
class TypeNode(ASTNode[S, P], Generic[S, P]):
    """型表記の基底"""
    pass


@dataclass(repr=False)
class PrimitiveTypeNode(TypeNode[S, P], Generic[S, P]):
    """
    組み込み
    """
    # ここでトークン種別を再利用
    type_type: TokenType


@dataclass(repr=False)
class UserDefinedTypeNode(TypeNode[S, P], Generic[S, P]):
    """
    自作クラス
    """
    name: str

@dataclass(repr=False)
class ArrayTypeNode(TypeNode[S, P], Generic[S, P]):
    """
    あーりー
    """
    element_type: TypeNode[S, P]
    size: int


@dataclass(repr=False)
class ListTypeNode(TypeNode[S, P], Generic[S,P]):
    """
    りすと
    """
    element_type: TypeNode[S, P]