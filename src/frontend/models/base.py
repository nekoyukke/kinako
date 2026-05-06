from __future__ import annotations
from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, cast
from enum import Enum


S = TypeVar("S", bound="absSymbol")
P = TypeVar("P", bound="absPlace")


class absSymbol(ABC):
    """
    Symbol実体
    src.core.symbol.symbolから継承
    """

    @property
    @abstractmethod
    def fq_name(self) -> str: ...


@dataclass(frozen=True)
class absProjection(ABC):
    """
    パスの履歴
    core.place.projection
    """
    @property
    @abstractmethod
    def get_main(self) -> absSymbol: ...


class absPlace(ABC):
    """
    Placeの実体。
    core.place.Place
    """
    @property
    @abstractmethod
    def get_main(self) -> absSymbol: ...
    
    @property
    @abstractmethod
    def get_projections(self) -> list[absProjection]: ...


@dataclass
class ASTNode(Generic[S, P]):
    """
    ASTノードの基底
    """
    line: int
    col: int
    len: int

    def _format_repr(self, indent: int = 0) -> str:
        """再帰的に整形されたAST表現を生成する"""
        indent_str = "  " * indent
        next_indent_str = "  " * (indent + 1)
        
        class_name = self.__class__.__name__
        
        # フィールドを取得
        try:
            node_fields = fields(self)
        except TypeError:
            # dataclassではない場合は標準のreprを返す
            return object.__repr__(self)
        
        if not node_fields:
            return f"{class_name}()"
        
        field_strs: list[str] = []
        for f in node_fields:
            # line, column, len フィールドをスキップ
            
            value = getattr(self, f.name)
            formatted_value = self._format_value(value, indent + 1)
            
            # 値が複数行の場合は改行を入れる
            if "\n" in formatted_value:
                field_strs.append(f"{f.name}=\n{next_indent_str}{formatted_value}")
            else:
                field_strs.append(f"{f.name}={formatted_value}")
        
        # フィールド数が多い場合は各フィールドを改行する
        if len(field_strs) > 2 or any("\n" in fs for fs in field_strs):
            fields_str = f",\n{next_indent_str}".join(field_strs)
            return f"{class_name}(\n{next_indent_str}{fields_str}\n{indent_str})"
        else:
            return f"{class_name}({', '.join(field_strs)})"
    
    def _format_value(self, value: list[Any] | Any, indent: int) -> str:
        """値を適切にフォーマットする"""
        indent_str = "  " * indent
        next_indent_str = "  " * (indent + 1)
        
        # None
        if value is None:
            return "None"
        
        # ASTNode（再帰）
        if isinstance(value, ASTNode):
            return value._format_repr(indent=indent)
        
        # Enum
        if isinstance(value, Enum):
            return f"{value.__class__.__name__}.{value.name}"
        
        # リスト
        if isinstance(value, list):
            if not value:
                return "[]"
            nvalue: list[Any] = cast(list[Any], value)
            # 要素が複数またはASTNodeを含む場合は改行
            formatted_items: list[str] = [self._format_value(item, indent + 1) for item in nvalue]
            if len(nvalue) > 2 or any(isinstance(v, ASTNode) for v in nvalue):
                items_str = f",\n{next_indent_str}".join(formatted_items)
                return f"[\n{next_indent_str}{items_str}\n{indent_str}]"
            else:
                return f"[{', '.join(formatted_items)}]"
        
        # 文字列
        if isinstance(value, str):
            return repr(value)
        
        # 数値、真偽値など
        return repr(value)
    
    def __repr__(self) -> str:
        return self._format_repr(indent=0)