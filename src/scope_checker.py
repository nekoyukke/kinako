from dataclasses import dataclass, field
from typing import Optional, Dict

from src.myast import *
from src.utils import AnalysisError, logging
from src.tokens import *
from src.type import *
from src.myast import *
from src.parser import *
from src.tokens import *
from src.lexer import tokenize
from src.borrow import *

@dataclass
class Scope:
    symbols: Dict[str, Symbol] = field(default_factory=dict[str, Symbol]) # 内部のシンボル
    parent: Optional["Scope"] = None # 親
    name: str = "Global"
    def deep(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.deep() + 1


# スコープのチェック
class ScopeChecker:
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.Symbol: list[Symbol] = []
        self.Scope: Scope
        self.source = source
        self.blocknum:int = 0
        self.visited_imports: set[str] = set() # コロコロしちゃったとこ
        self.current_file_path = ""
        """
        class A{
            let int a; // a
            fn func{} // func
        }
        """
    
    def _util_CallError(self, message: str, line: int, column: int, name: str, len: int) -> None:
        raise AnalysisError(message, line, column, self.source, name, len)

    def reset(self) -> None:
        self.Symbol = []
        self.Scope = Scope({}, None) # Global
        return
    
    def _util_this_fqname(self) -> str:
        scope = self.Scope
        names:list[str] = []
        while scope is not None:
            if scope.name:
                names.append(scope.name)
            scope = scope.parent
        names.append("__main__file")
        names.reverse()
        return ".".join(names)

    def visit_Scope_Check(self) -> Program:
        self.__visit_Scope_Check()
        return self.node
    
    def __visit_Scope_Check(self) -> None:
        # Todo
        # ここでやることは
        # *新しい宣言->Symbol追加
        # *変数の使用->Symbol参照（メソッド越し）
        # *BlockによるScope調整
        """
        DeclarationNode
        ExprStmtNode
        BlockNode
        IfStmtNode
        WhileStmtNode
        FunctionDefNode
        ReturnStmtNode
        ClassDefNode
        ForNode
        ImportNode
        """
        for i in self.node.import_stmt:
            self.__visit_Node(i)
        blocks:list[Stmt] = []
        for i in self.node.imports:
            blocks += i.blocks
        self.node.blocks = blocks + self.node.blocks
        for i in self.node.blocks:
            # matchで分岐
            self.__visit_Node(i)
        
    def __visit_Node(self, i:Stmt):
        match (i):
            # 定義系
            case DeclarationNode():
                return self._visit_Declaration(i)
            case FunctionDefNode():
                return self._visit_FunctionDef(i)
            case ImportNode():
                return self._visit_Import(i)
            case ClassDefNode():
                return self._visit_ClassDef(i)
            # Exprに飛ぶ系
            case ExprStmtNode():
                return self._visit_ExprStmt(i)
            case ReturnStmtNode():
                return self._visit_ReturnStmt(i)
            # この中のblockをwhileで再帰して回す系
            case WhileStmtNode():
                return self._visit_WhileStmt(i)
            case BlockNode():
                return self._visit_Block(i)
            case IfStmtNode():
                return self._visit_IfStmt(i)
            case ForNode():
                return self._visit_For(i)
            case _:
                # unknown node
                # 例外だしても、、いいよね？
                raise
        
    def _util_Symbolapp(self, symbol:Symbol, node:DeclarationNode | ClassDefNode | FunctionDefNode | ImportNode | ForNode):
        node.symbol = symbol
        self.Symbol.append(symbol)
        self.Scope.symbols[symbol.name] = symbol
        return None
    
    def _util_make_Scope(self, scope:Scope):
        if scope.parent is not None:
            self.Scope = scope
            return
        scope.parent = self.Scope
        self.Scope = scope
    
    def _visit_Param(self, Param:Params, node:FunctionDefNode):
        symbol = Symbol(
            Param.name.name,
            self._util_this_fqname() + "." + Param.name.name,
            node,
            Param.types,
            False,
            deep=self.Scope.deep()
        )
        Param.name.symbol = symbol
        self.Symbol.append(symbol)
        self.Scope.symbols[symbol.name] = symbol
    
    def _util_Scope_pop(self):
        if self.Scope.parent is None:
            logging.warning("Error! Parent is none. in scope checker")
            return
        self.Scope = self.Scope.parent

    def _visit_Declaration(self, node:DeclarationNode) -> None:
        if node.right is not None:
            self._visit_expr(node.right)
        # 同じ階層でかぶっているか
        if node.left.name in self.Scope.symbols:
            symbolnode = self.Scope.symbols[node.left.name].node
            self._util_CallError(
                f"The variable name '{node.left.name}' is already in use at line:{symbolnode.line},column:{symbolnode.column}. line:{node.line},column:{node.column}",
                node.line,
                node.column,
                "_visit_Declaration",
                node.len
            )
        symbol = Symbol(
            node.left.name,
            self._util_this_fqname() + "." + node.left.name,
            node,
            node.type,
            False,
            deep=self.Scope.deep()
        )
        node.symbol = symbol
        node.left.symbol = symbol
        self._util_Symbolapp(symbol, node)
        return

    def _visit_FunctionDef(self, node:FunctionDefNode) -> None:
        if node.name.String in self.Scope.symbols:
            symbolnode = self.Scope.symbols[node.name.String].node
            self._util_CallError(
                f"The variable name '{node.name.String}' is already in use at line:{symbolnode.line},column:{symbolnode.column}. line:{node.line},column:{node.column}",
                node.line,
                node.column,
                "_visit_FunctionDef",
                node.len
            )
            raise
        symbol = Symbol(
            node.name.String,
            self._util_this_fqname() + "." + node.name.String,
            node,
            node.type,
            False,
            deep=self.Scope.deep()
        )
        self._util_Symbolapp(symbol, node)
        # スコープ作成
        self._util_make_Scope(Scope(name = node.name.String + "_func"))
        for param in node.params:
           self._visit_Param(param, node)
        # スコープ名前解決
        self.__visit_Node(node.body)
        # スコープ削除
        self._util_Scope_pop()
        return


    def _visit_Import(self, node:ImportNode) -> None:
        import os

        base = os.path.dirname(self.current_file_path)
        path = os.path.normpath(os.path.join(base, node.From.string))
        abs_path = os.path.abspath(path)

        if abs_path in self.visited_imports:
            return

        self.visited_imports.add(abs_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Import file not found: {abs_path}")

        with open(abs_path, encoding="utf-8") as f:
           source = f.read()

        toks = tokenize(source)
        asts = ast(toks, source)
        sc = ScopeChecker(asts, source)
        sc.reset()
        sc.visited_imports = self.visited_imports
        sc.visit_Scope_Check()
        self.Symbol += sc.Symbol
        self.node.imports += [asts]
        self.node.import_stmt.remove(node)

    def _visit_ClassDef(self, node:ClassDefNode) -> None:
        # まだ未実装
        return

    def _visit_ExprStmt(self, node:ExprStmtNode) -> None:
        self._visit_expr(node.expr)
        # たったこれだけ
        return

    def _visit_ReturnStmt(self, node:ReturnStmtNode) -> None:
        self._visit_expr(node.value)
        # たったこれだけ(二回目)
        return

    def _visit_WhileStmt(self, node:WhileStmtNode) -> None:
        # while
        self._visit_expr(node.condition)
        if type(node.body) == BlockNode:
            self._visit_Block(node.body)
            return
        self._util_make_Scope(Scope(name=f"{self.blocknum}_Block"))
        self.blocknum+=1
        self.__visit_Node(node.body)
        self._util_Scope_pop()
        return

    def _visit_Block(self, node:BlockNode) -> None:
        # ブロック作ってstmt回してる
        self._util_make_Scope(Scope(name=f"{self.blocknum}_Block"))
        self.blocknum += 1
        for stmt in node.blocks:
            self.__visit_Node(stmt)
        self._util_Scope_pop()

    def _visit_IfStmt(self, node:IfStmtNode) -> None:
        self._visit_expr(node.condition)
        if type(node.then_block) == BlockNode:
            self._visit_Block(node.then_block)
        else:
            self._util_make_Scope(Scope(name=f"{self.blocknum}_Block"))
            self.blocknum+=1
            self.__visit_Node(node.then_block)
            self._util_Scope_pop()
        if node.else_block is None:
            return

        if type(node.else_block) == BlockNode:
            self._visit_Block(node.else_block)
        else:
            self._util_make_Scope(Scope(name=f"{self.blocknum}_Block"))
            self.blocknum+=1
            self.__visit_Node(node.else_block)
            self._util_Scope_pop()
        return
    
    def _visit_ForParam(self, name: VariableNode, node:ForNode) -> None:
        symbol = Symbol(
            name.name,
            self._util_this_fqname() + "." + name.name,
            node,
            None,
            False,
            deep=self.Scope.deep()
        )
        name.symbol = symbol
        self.Symbol.append(symbol)
        self.Scope.symbols[symbol.name] = symbol

    def _visit_For(self, node: ForNode) -> None:
        self._util_make_Scope(Scope(name=f"For_{self.blocknum}"))
        self.blocknum += 1

        self._visit_ForParam(node.iterator, node)

        self._visit_expr(node.iterable)

        if isinstance(node.body, BlockNode):
            self._visit_Block(node.body)
        else:
            self._util_make_Scope(Scope(name=f"ForBody_{self.blocknum}"))
            self.blocknum += 1
            self.__visit_Node(node.body)
            self._util_Scope_pop()
        self._util_Scope_pop()
    
    def _visit_expr(self, node:Optional[Expr]) -> None:
        # これもmatchで回して演算ならまたexpr回す
        # 正直言ってVal以外passでret
        if node is None:
            return
        match (node):
            case BinaryOpNode():
                self._visit_expr(node.left)
                self._visit_expr(node.right)
                return
            case UnaryOpNode():
                self._visit_expr(node.right)
                return
            case AssignNode():
                # 変更可能かどうか
                if not isinstance(node.left, (VariableNode, MemberAccessNode, IndexAccessNode, UnaryOpNode)):
                    self._util_CallError(
                        "Left side of assignment is not assignable",
                        node.op.line,
                        node.op.column,
                        "_visit_Assign",
                        len(node.op.String)
                    )
                if isinstance(node.left, UnaryOpNode):
                    if not node.left.op.type in (TokenType.MULT, TokenType.ADD):
                        self._util_CallError(
                            "Left side of assignment is not assignable",
                            node.op.line,
                            node.op.column,
                            "_visit_Assign",
                            len(node.op.String)
                        )
                self._visit_expr(node.right)
                self._visit_expr(node.left)
                return
            case CallExprNode():
                # 呼び出し
                self._visit_expr(node.func_name)
                for i in node.args:
                    self._visit_expr(i)
                return
            case MemberAccessNode():
                # メンバアクセス。ちょっとめんどい処理
                self._visit_expr(node.left)
                if not isinstance(node.left, MemberAccessNode | VariableNode):
                    # 型に対する侮辱
                    self._util_CallError("左辺が不明です.", node.line, node.column, "", node.len)
                    raise
                if node.left.symbol is None:
                    raise
                node.symbol = node.right.symbol
                return
            case IndexAccessNode():
                self._visit_expr(node.addr)
                self._visit_expr(node.index)
                return
            case AsCastNode():
                self._visit_expr(node.obj)
                return
            case VariableNode():
                # 存在するかどうかの検知
                name = node.name
                scope = self.Scope

                while scope is not None:
                    if name in scope.symbols:
                        node.symbol = scope.symbols[name]
                        node.now_deep = self.Scope.deep()
                        logging.debug(node.symbol)
                        return
                    scope = scope.parent
                # 見つからなかった
                logging.debug(self.Scope)
                self._util_CallError(
                    f"Undefined variable '{name}'",
                    node.token.line,
                    node.token.column,
                    "_visit_Variable",
                    len(name)
                )
                raise
            case MoveOpNode():
                self._visit_expr(node.right)
                return
            case BorrowOpNode():
                self._visit_expr(node.right)
                return
            case ReferenceNode():
                self._visit_expr(node.right)
                return

            case DereferenceNode():
                self._visit_expr(node.right)
                return
            case _:
                return