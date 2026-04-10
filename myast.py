from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import List, Optional, Any
from tokens import Token
from enum import Enum
from type import TypeObject

class Borrow(Enum):
    NONE = 0 # 無効
    MOVED = 1 # 移動済み
    UNINIT = 2 # 初期化なし
    ACTIVE = 3 # 有効
    BORROWED = 4 # 借りられている
    BORROW = 5 # 借りている

@dataclass
class AnalysisBorrow():
    borrow:Borrow
    from_:Symbol

# 解析用
@dataclass
class Symbol:
    name: str
    fq_name: str
    node: DeclarationNode | ClassDefNode | FunctionDefNode | ImportNode | ForNode # 関数定義ノードや変数定義ノード
    type: Optional[TypeNode] = None # 型
    is_extern: bool = False # 外部
    member: list[Symbol] = field(default_factory=list["Symbol"])
    Type_analysis: Optional[TypeObject] = None # 型
    borrow_state:Borrow = Borrow.NONE



@dataclass
class ASTNode:
    def __repr__(self) -> str:
        return self._format_repr(indent=0)
    
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
            if f.name in ('line', 'column', 'len'):
                continue
            
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
    
    def _format_value(self, value: Any, indent: int) -> str:
        """値を適切にフォーマットする"""
        indent_str = "  " * indent
        next_indent_str = "  " * (indent + 1)
        
        # None
        if value is None:
            return "None"
        
        # ASTNode（再帰）
        if isinstance(value, ASTNode):
            return value._format_repr(indent=indent)
        
        # Symbol（再帰ループを避けるため浅い表示）
        if isinstance(value, Symbol):
            return f"Symbol(name={value.name!r}, fq_name={value.fq_name!r})"
        
        # Token
        if isinstance(value, Token):
            return f"Token({value.type.name}, {value.value!r}, L{value.line}:{value.column})"
        
        # Enum
        if isinstance(value, Enum):
            return f"{value.__class__.__name__}.{value.name}"
        
        # リスト
        if isinstance(value, list):
            if not value:
                return "[]"
            # 要素が複数またはASTNodeを含む場合は改行
            formatted_items: list[str] = [self._format_value(item, indent + 1) for item in value]
            if len(value) > 2 or any(isinstance(v, ASTNode) for v in value):
                items_str = f",\n{next_indent_str}".join(formatted_items)
                return f"[\n{next_indent_str}{items_str}\n{indent_str}]"
            else:
                return f"[{', '.join(formatted_items)}]"
        
        # 文字列
        if isinstance(value, str):
            return repr(value)
        
        # 数値、真偽値など
        return repr(value)

# --- Typenode(型) ---

@dataclass(repr=False)
class TypeNode(ASTNode):
    # 型
    type_name: str
    token: Token
    is_dynamic: bool

@dataclass(repr=False)
class ListTypeNode(TypeNode):
    # リスト
    element_type: TypeNode
    def __repr__(self) -> str:
        return f"List<{self.element_type}>"

@dataclass(repr=False)
class PointerTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass(repr=False)
class MutTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass(repr=False)
class BorrowTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass(repr=False)
class FunctionTypeNode(TypeNode):
    # 関数タイプ
    param_types: List[TypeNode]
    return_type: Optional[TypeNode]

@dataclass(repr=False)
class Params(ASTNode):
    # int aなどの形
    types: TypeNode
    name: VariableNode

class ClassVariable(Enum):
    STATIC = 0
    PRIVATE = 1
    PUBLIC = 2
    INHERITANCE = 3

@dataclass(repr=False)
class ClassFunctionParams(ASTNode):
    ft: FunctionTypeNode
    f: FunctionDefNode
    cv: ClassVariable

@dataclass(repr=False)
class ClassVariableParams(ASTNode):
    # int aなどの形
    types: TypeNode
    literal: Literal
    cv: ClassVariable


# --- Expressions (値を返す) ---
@dataclass(repr=False)
class Expr(ASTNode):
    line: int
    column: int
    len: int

@dataclass(repr=False)
class Literal(Expr):
    pass

@dataclass(repr=False)
class NumberNode(Literal):
    # 数字
    value: int
    token: Token
    base: int

@dataclass(repr=False)
class DecimalNode(Literal):
    # 数字
    value: float
    token: Token

@dataclass(repr=False)
class VariableNode(Literal):
    # 変数
    name: str
    token: Token
    symbol: Optional[Symbol] = None


@dataclass(repr=False)
class StringNode(Literal):
    # 文字列
    string: str
    token: Token

@dataclass(repr=False)
class NullNode(Literal):
    # null
    token: Token

@dataclass(repr=False)
class NoneNode(Literal):
    # none
    token: Token

@dataclass(repr=False)
class BoolNode(Literal):
    # 真偽値
    token: Token
    flag: bool

@dataclass(repr=False)
class LifetimeNode(Literal):
    # ライフなタイム
    name: str
    token: Token

@dataclass(repr=False)
class BinaryOpNode(Expr):
    # 2項演算
    left: Expr
    op: Token
    right: Expr

@dataclass(repr=False)
class UnaryOpNode(Expr):
    # 単項演算
    op: Token
    right: Expr

@dataclass(repr=False)
class BorrowOpNode(Expr):
    right: Expr
    
@dataclass(repr=False)
class MoveOpNode(Expr):
    right: Expr

class AssginType(Enum):
    ASSIGN = "="
    ADD_ASSIGN = "+="
    SUB_ASSIGN = "-="
    MUL_ASSIGN = "*="
    DIV_ASSIGN = "/="
    DIVV_ASSIGN = "//="
    MOD_ASSIGN = "%="
    NULLCOALESCING_ASSIGN = "?="
    NONECOALESCING_ASSIGN = "%%="

@dataclass(repr=False)
class AssignNode(Expr):
    # 等号
    left: Expr
    right: Expr
    op: Token
    type: AssginType

@dataclass(repr=False)
class CallExprNode(Expr):
    # 呼び出し
    func_name: Expr
    args: List[Expr]

@dataclass(repr=False)
class MemberAccessNode(Expr):
    left: Expr
    right: VariableNode
    symbol: Optional[Symbol] = None

@dataclass(repr=False)
class IndexAccessNode(Expr):
    addr: Expr
    index: Expr

@dataclass(repr=False)
class AsCastNode(Expr):
    obj: Expr
    type: TypeNode

# --- Statements (処理を行う) ---
@dataclass(repr=False)
class Stmt(ASTNode):
    line: int
    column: int
    len: int

class VariableType(Enum):
    CONST = 0
    VAL = 1
    LET = 2
    MUT = 3
    BORROW = 4

@dataclass(repr=False)
class DeclarationNode(Stmt):
    # 定義
    
    left: VariableNode
    right: Optional[Expr]
    type: TypeNode
    vartype: VariableType
    symbol: Optional[Symbol] = None

@dataclass(repr=False)
class ExprStmtNode(Stmt):
    
    # 文字だけどstmt
    expr: Expr

@dataclass(repr=False)
class BlockNode(Stmt):
    
    # ブロック
    blocks: List[Stmt]

@dataclass(repr=False)
class IfStmtNode(Stmt):
    
    # if文
    condition: Expr
    then_block: Stmt
    else_block: Optional[Stmt] = None

@dataclass(repr=False)
class WhileStmtNode(Stmt):
    
    # 繰り返し
    condition: Expr
    body: Stmt
    else_block: Optional[Stmt] = None

@dataclass(repr=False)
class FunctionDefNode(Stmt):
    # 関数定義
    
    name: Token
    body: Stmt
    type: FunctionTypeNode
    params: list[Params]
    symbol: Optional[Symbol] = None

@dataclass(repr=False)
class ReturnStmtNode(Stmt):
    
    # 返る
    token: Token
    value: Optional[Expr] = None

@dataclass(repr=False)
class ClassDefNode(Stmt):
    # 定義
    
    name: Token
    variable: list[ClassVariableParams]
    method: list[ClassFunctionParams]
    extends: Optional[list[Token]] = None
    symbol: Optional[Symbol] = None

@dataclass(repr=False)
class Program(Stmt):
    blocks: list[Stmt]

@dataclass(repr=False)
class ForNode(Stmt):
    
    iterator: VariableNode
    iterable: Expr
    body: Stmt
    symbol: Optional[Symbol] = None

@dataclass(repr=False)
class ImportNode(Stmt):
    
    From: Expr
    Import: Token
    symbol: Optional[Symbol] = None