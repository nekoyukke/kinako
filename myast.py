from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from tokens import Token
from enum import Enum
from type import TypeObject
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



@dataclass
class ASTNode:
    pass

# --- Typenode(型) ---

@dataclass
class TypeNode(ASTNode):
    # 型
    type_name: str
    token: Token
    is_dynamic: bool

@dataclass
class ListTypeNode(TypeNode):
    # リスト
    element_type: TypeNode

@dataclass
class PointerTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass
class MutTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass
class BorrowTypeNode(TypeNode):
    # ポインタ
    element_type: TypeNode

@dataclass
class FunctionTypeNode(TypeNode):
    # 関数タイプ
    param_types: List[TypeNode]
    return_type: Optional[TypeNode]

@dataclass
class Params(ASTNode):
    # int aなどの形
    types: TypeNode
    name: VariableNode

class ClassVariable(Enum):
    STATIC = 0
    PRIVATE = 1
    PUBLIC = 2
    INHERITANCE = 3

@dataclass
class ClassFunctionParams(ASTNode):
    ft: FunctionTypeNode
    f: FunctionDefNode
    cv: ClassVariable

@dataclass
class ClassVariableParams(ASTNode):
    # int aなどの形
    types: TypeNode
    literal: Literal
    cv: ClassVariable


# --- Expressions (値を返す) ---
@dataclass
class Expr(ASTNode):
    line: int
    column: int
    len: int

@dataclass
class Literal(Expr):
    pass

@dataclass
class NumberNode(Literal):
    # 数字
    value: int
    token: Token
    base: int

@dataclass
class VariableNode(Literal):
    # 変数
    name: str
    token: Token
    symbol: Optional[Symbol] = None


@dataclass
class StringNode(Literal):
    # 文字列
    string: str
    token: Token

@dataclass
class NullNode(Literal):
    # null
    token: Token

@dataclass
class NoneNode(Literal):
    # none
    token: Token

@dataclass
class BoolNode(Literal):
    # 真偽値
    token: Token
    flag: bool

@dataclass
class LifetimeNode(Literal):
    # ライフなタイム
    name: str
    token: Token

@dataclass
class BinaryOpNode(Expr):
    # 2項演算
    left: Expr
    op: Token
    right: Expr

@dataclass
class UnaryOpNode(Expr):
    # 単項演算
    op: Token
    right: Expr

@dataclass
class LogicalOpNode(Expr):
    # 真偽値用の演算
    left: Expr
    op: Token
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

@dataclass
class AssignNode(Expr):
    # 等号
    left: Expr
    right: Expr
    op: Token
    type: AssginType

@dataclass
class CallExprNode(Expr):
    # 呼び出し
    func_name: Expr
    args: List[Expr]

@dataclass
class MemberAccessNode(Expr):
    left: Expr
    right: VariableNode

@dataclass
class IndexAccessNode(Expr):
    addr: Expr
    index: Expr

@dataclass
class AsCastNode(Expr):
    obj: Expr
    type: TypeNode

# --- Statements (処理を行う) ---
@dataclass
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

@dataclass
class DeclarationNode(Stmt):
    # 定義
    
    left: VariableNode
    right: Optional[Expr]
    type: TypeNode
    vartype: VariableType
    symbol: Optional[Symbol] = None

@dataclass
class ExprStmtNode(Stmt):
    
    # 文字だけどstmt
    expr: Expr

@dataclass
class BlockNode(Stmt):
    
    # ブロック
    blocks: List[Stmt]
    lifetime: Optional[LifetimeNode]
    captures: list[VariableNode]

@dataclass
class IfStmtNode(Stmt):
    
    # if文
    condition: Expr
    then_block: Stmt
    else_block: Optional[Stmt] = None

@dataclass
class WhileStmtNode(Stmt):
    
    # 繰り返し
    condition: Expr
    body: Stmt
    else_block: Optional[Stmt] = None

@dataclass
class FunctionDefNode(Stmt):
    # 関数定義
    
    name: Token
    body: Stmt
    type: FunctionTypeNode
    params: list[Params]
    symbol: Optional[Symbol] = None

@dataclass
class ReturnStmtNode(Stmt):
    
    # 返る
    token: Token
    value: Optional[Expr] = None

@dataclass
class ClassDefNode(Stmt):
    # 定義
    
    name: Token
    variable: list[ClassVariableParams]
    method: list[ClassFunctionParams]
    extends: Optional[list[Token]] = None
    symbol: Optional[Symbol] = None

@dataclass
class Program(Stmt):
    blocks: list[Stmt]

@dataclass
class ForNode(Stmt):
    
    iterator: VariableNode
    iterable: Expr
    body: Stmt
    symbol: Optional[Symbol] = None

@dataclass
class ImportNode(Stmt):
    
    From: Expr
    Import: Token
    symbol: Optional[Symbol] = None