from dataclasses import dataclass, field
from typing import Optional, Dict
from myast import *
from utils import AnalysisError, logging

@dataclass
class Scope:
    symbols: Dict[str, Symbol] = field(default_factory=dict[str, Symbol]) # 内部のシンボル
    aliases: Dict[str, str] = field(default_factory=dict[str, str]) # 外部の制限
    parent: Optional["Scope"] = None # 親
    name: str = "Global"

# Checker統合
class LangageChecker:
    def __init__(self, node:Program) -> None:
        pass

# スコープのチェック
class ScopeChecker:
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.Symbol: list[Symbol] = []
        self.Scope: Scope
        self.source = source
        self.std: dict[str, dict[str, dict[str, Symbol]]] = {}
        self.blocknum:int = 0
    
    def _util_CallError(self, message: str, line: int, column: int, name: str, len: int) -> None:
        raise AnalysisError(message, line, column, self.source, name, len)

    def reset(self) -> None:
        self.Symbol = []
        self.std = self._util_std_load()
        self.Scope = Scope({}, {}, None) # Global
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
        blocks: list[Stmt] = self.node.blocks
        for i in blocks:
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
        
    def _util_std_load(self):
        import std.std
        return std.std.STD
    
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
            node.type,
            False
        )
        self._util_Symbolapp(symbol, node)
    
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
            False
        )
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
        symbol = Symbol(
            node.name.String,
            self._util_this_fqname() + "." + node.name.String + "_",
            node,
            node.type,
            False
        )
        self._util_Symbolapp(symbol, node)
        # スコープ作成
        self._util_make_Scope(Scope(name = node.name.String + "_func"))
        for param in node.params:
           self._visit_Param(param, node)
        # スコープ名前解決
        self.__visit_Node(node.body)
        self._util_Scope_pop()
        return

    def _visit_import_module_path(self, node:Expr, importtok:Token) -> list[str]:
        if type(node) == MemberAccessNode:
            return self._visit_import_module_path(node.left, importtok) + [node.right.name]
        if type(node) == VariableNode:
            return [node.token.String]
        else:
            self._util_CallError("unknown Token of import path", importtok.line, importtok.column, "import path", importtok.String.__len__())
            raise

    def _visit_Import(self, node:ImportNode) -> None:
        path = self._visit_import_module_path(node.From, node.Import)
        module = self.std
        for p in path:
            if p not in module:
                self._util_CallError(
                    f"Module '{'.'.join(path)}' not found{path}",
                    node.line,
                    node.column,
                    "_visit_Import",
                    node.len
                )
            module = module[p]

        name = path[-1] # std, io, print

        if name in self.Scope.symbols:
            prev = self.Scope.symbols[name].node
            self._util_CallError(
                f"'{name}' is already defined at line:{prev.line},column:{prev.column}.",
                node.line,
                node.column,
                "_visit_Import",
                node.len
            )

        fq = ".".join(path)  # "std.io.print"
        symbol = Symbol(
            name=name,
            fq_name=fq,
            node=node,
            type=None,  # モジュール型があるなら入れる
            is_extern=True
        )

        self._util_Symbolapp(symbol, node)
        node.symbol = symbol

        return

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
        self._util_make_Scope(Scope(aliases={}, name=f"{self.blocknum}_Block"))
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
            False
        )
        self._util_Symbolapp(symbol, node)

    def _visit_For(self, node: ForNode) -> None:
        self._util_make_Scope(Scope(name=f"For_{self.blocknum}"))
        self.blocknum += 1

        if node.iterator:
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
            case LogicalOpNode():
                self._visit_expr(node.right)
                self._visit_expr(node.left)
                return
            case AssginNode():
                self._visit_expr(node.right)
                self._visit_expr(node.left)
                return
            case CallExprNode():
                self._visit_expr(node.func_name)
                for i in node.args:
                    self._visit_expr(i)
                return
            case MemberAccessNode():
                self._visit_expr(node.left)
                return
            case IndexAccessNode():
                self._visit_expr(node.addr)
                self._visit_expr(node.index)
                return
            case VariableNode():
                # 存在するかどうかの検知
                name = node.name
                scope = self.Scope

                while scope is not None:
                    if name in scope.symbols:
                        node.symbol = scope.symbols[name]
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
            case _:
                return
        return
    

# 型のチェック
# 演算・代入・暗黙変換
class TypeChecker:
    def __init__(self, node:Program) -> None:
        pass

# 汎用変数のブロック外へのアクセス制限
class EscapeAnalyzer:
    def __init__(self) -> None:
        pass

# 借用チェック
class BorrowingChecker:
    def __init__(self, node:Program) -> None:
        pass
