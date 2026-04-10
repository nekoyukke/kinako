from dataclasses import dataclass, field
from typing import Optional, Dict
from myast import *
from utils import AnalysisError, logging
from tokens import *
from type import *

@dataclass
class Scope:
    symbols: Dict[str, Symbol] = field(default_factory=dict[str, Symbol]) # 内部のシンボル
    parent: Optional["Scope"] = None # 親
    name: str = "Global"


# スコープのチェック
class ScopeChecker:
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.Symbol: list[Symbol] = []
        self.Scope: Scope
        self.source = source
        self.std: dict[str, dict[str, dict[str, Symbol]]] = {}
        self.blocknum:int = 0
        self.classdata: dict[str, Symbol]
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
        self.std = self._util_std_load()
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
            Param.types,
            False
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
            raise
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
        # スコープ削除
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
            False
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
                    return
                if node.left.symbol is None:
                    raise
                if node.left.symbol.is_extern:
                    fq_parts = node.left.symbol.fq_name.split(".")
                    module = self.std
                    try:
                        for part in fq_parts:
                            module = module[part]
                        if isinstance(module, Symbol):
                            raise
                        if node.right.name in module:
                            node.symbol = module[node.right.name]
                        else:
                            self._util_CallError(
                                f"Undefined member '{node.right.name}' in '{node.left.symbol.fq_name}'",
                                node.line,
                                node.column,
                                "_visit_MemberAccess",
                                len(node.right.name)
                            )
                    except KeyError:
                        self._util_CallError(
                            f"Module '{node.left.symbol.fq_name}' not found",
                            node.line,
                            node.column,
                            "_visit_MemberAccess",
                            len(node.left.symbol.fq_name)
                        )
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
            case _:
                return


# 型のチェック
# 演算・代入・暗黙変換
class TypeChecker:
    import std.stdclass
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.source = source
        self.current_return_type: None | TypeObject = None
        self.return_types: list[TypeObject] = []
    
    def _util_CallError(self, message: str, line: int, column: int, name: str, len: int) -> AnalysisError:
        raise AnalysisError(message, line, column, self.source, name, len)

    def _util_CallWarn(self, message: str, line: int, column: int, name: str, len: int) -> None:
        print("警告" + AnalysisError(message, line, column, self.source, name, len).__str__())

    def visit_TypeCheck(self):
        return self.__visit_typecheck()
    
    def __visit_typecheck(self):
        for i in self.node.blocks:
            self.__visit_Stmtnode(i)

    def _util_Typenode2type(self, node:TypeNode) -> TypeObject:
        match (node):
            case ListTypeNode():
                return TypeList(self._util_Typenode2type(node.element_type))
            case PointerTypeNode():
                return TypePtr(self._util_Typenode2type(node.element_type))
            case FunctionTypeNode():
                if node.return_type is None:
                    return TypeFunction(
                        [self._util_Typenode2type(i) for i in node.param_types],
                        TypeNone(),
                    )
                return TypeFunction(
                    [self._util_Typenode2type(i) for i in node.param_types],
                    self._util_Typenode2type(node.return_type)
                )
            case FunctionTypeNode():
                if node.return_type is None:
                    return TypeFunction(
                        [self._util_Typenode2type(i) for i in node.param_types],
                        TypeNone()
                    )
                return TypeFunction(
                    [self._util_Typenode2type(i) for i in node.param_types],
                    self._util_Typenode2type(node.return_type)
                )
            case TypeNode():
                match (node.token.type):
                    case TokenType.tNUM:
                        return TypeInt(None, True, True)
                    case TokenType.tDEC:
                        return TypeFloat(None, True)
                    case TokenType.tSTR:
                        return TypeString()
                    case TokenType.tANY:
                        return TypeAny()
                    case TokenType.tARRAY:
                        # 未実装なり～
                        raise
                    case TokenType.tDYNAMIC:
                        # 型推論型
                        return TypeDynamic()
                    case TokenType.tMAP:
                        # 未実装なり～
                        raise
                    case TokenType.tBOOL:
                        return TypeBool()
                    case TokenType.tCLASS:
                        # みじっそう
                        raise
                    case TokenType.tANYNUMBER:
                        # 廃止
                        raise
                    case TokenType.tANYFLOAT:
                        # 廃止
                        raise
                    case TokenType.tINT8:
                        return TypeInt(8, False, True)
                    case TokenType.tUINT8:
                        return TypeInt(8, False, False)
                    case TokenType.tINT16:
                        return TypeInt(16, False, True)
                    case TokenType.tUINT16:
                        return TypeInt(16, False, False)
                    case TokenType.tINT32:
                        return TypeInt(32, False, True)
                    case TokenType.tUINT32:
                        return TypeInt(32, False, False)
                    case TokenType.tINT64:
                        return TypeInt(64, False, True)
                    case TokenType.tUINT64:
                        return TypeInt(64, False, False)
                    case TokenType.tINT128:
                        return TypeInt(128, False, True)
                    case TokenType.tUINT128:
                        return TypeInt(128, False, False)
                    case TokenType.tFLOAT32:
                        return TypeFloat(32, False)
                    case TokenType.tFLOAT64:
                        return TypeFloat(64, False)
                    case TokenType.tFLOAT:
                        return TypeFloat(32, False)
                    case TokenType.tDOUBLE:
                        return TypeFloat(64, False)
                    case TokenType.tINT:
                        return TypeInt(32, False, True)
                    case TokenType.tLONG:
                        return TypeInt(64, False, True)
                    case TokenType.tSHORT:
                        return TypeInt(16, False, True)
                    case TokenType.tCHAR:
                        return TypeInt(8, False, True)
                    case TokenType.NONE:
                        return TypeNone()
                    case TokenType.NULL:
                        return TypeNull()
                    case _:
                        raise RuntimeError(node)
            case _:
                raise
        
    def __visit_Stmtnode(self, node:Stmt) -> bool:
        match (node):
            # 定義系
            case DeclarationNode():
                return self._visit_Declaration(node)
            case FunctionDefNode():
                return self._visit_FunctionDef(node)
            case ImportNode():
                return False
            case ClassDefNode():
                # 未実装
                return False
            # Exprに飛ぶ系
            case ExprStmtNode():
                self._visit_expr_(node.expr)
                return False
            case ReturnStmtNode():
                return self._visit_ReturnStmt(node)
            # この中のblockをwhileで再帰して回す系女子
            case WhileStmtNode():
                return self._visit_WhileStmt(node)
            case BlockNode():
                # むずい
                # いうほどじゃなかった
                return self._visit_BlockNode(node)
            case IfStmtNode():
                return self._visit_IfStmt(node)
            case ForNode():
                return self._visit_For(node)
            case _:
                # unknown node
                # 例外だしても、、いいよね？
                # い゛い゛よ゛！！
                # よくない、、、エラー出そ？（切実）
                raise
    
    def _visit_For(self, node:ForNode):
        # ああんいあうあい
        iterableType = self._visit_expr_(node.iterable)
        if node.iterator.symbol is None:
            raise
        if not isinstance(iterableType, Generic):
            # ゴミ
            raise self._util_CallError("イテラブルではありません", node.iterable.line, node.iterable.column, "", node.iterable.len)
        node.iterator.symbol.Type_analysis = iterableType.Generic
        self.__visit_Stmtnode(node.body)
        return False
    
    def _visit_IfStmt(self, node:IfStmtNode):
        # if else部どちらもTrueならTrueを返す。
        # そうでなければFalse
        cond = self._visit_expr_(node.condition)
        if not isinstance(cond, TypeBool):
            # これ
            raise self._util_CallError(f"{cond}とBooleanとでは型が合致しません", node.line, node.column, "", node.len)
        IsIf = False
        IsElse = False
        IsIf = self.__visit_Stmtnode(node.then_block)
        if not node.else_block is None:
            IsElse = self.__visit_Stmtnode(node.else_block)
        return IsIf and IsElse

    def _visit_BlockNode(self, node:BlockNode):
        cond = False
        for stmt in node.blocks:
            # stmtがどこかでTrueならTrueを返す
            cond = cond or self.__visit_Stmtnode(stmt)
        return cond
    
    def _visit_WhileStmt(self, node:WhileStmtNode) -> bool:
        condtype = self._visit_expr_(node.condition)
        if not isinstance(condtype, TypeBool):
            # これ
            raise self._util_CallError(f"{condtype}とBooleanとでは型が合致しません", node.line, node.column, "", node.len)
        self.__visit_Stmtnode(node.body)
        if node.else_block is not None:
            self.__visit_Stmtnode(node.else_block)
        return False

    def _visit_FunctionDef(self, node:FunctionDefNode) -> bool:
        # へへへ
        # スタックを呼ぶ
        ftn = node.type
        ft = self._util_Typenode2type(ftn)
        if not isinstance(ft, TypeFunction):
            raise self._util_CallError("不明な型情報", node.line, node.column, "", node.len)
        # 関数全体の型を Symbol に設定
        if node.symbol is None:
            raise self._util_CallError("関数のシンボルが設定されていません", node.line, node.column, "", node.len)
        node.symbol.Type_analysis = ft
        ft = ft.retype
        if not self.current_return_type is None:
            self.return_types.append(self.current_return_type)
        self.current_return_type = ft
        # 型データ追加
        for i in node.params:
            if i.name.symbol is None:
                raise
            i.name.symbol.Type_analysis = self._util_Typenode2type(i.types)
        # while
        IsRetStmt = self.__visit_Stmtnode(node.body)
        if IsRetStmt:
            # 戻った
            # OK
            pass
        else:
            # 戻らないので死
            raise self._util_CallError("すべてのコードパスで返り値が設定されていません", node.line, node.column, "", node.len)
        # スタックを戻す
        if self.return_types == []:
            # スタックないので
            self.current_return_type = None
        else:
            self.current_return_type = self.return_types[0]
            self.return_types.pop(0)
        return False

    def _visit_ReturnStmt(self, node:ReturnStmtNode) -> bool:
        # このよもすてたもんじゃないんだよ
        # node.value!!!
        # 帰ってください
        if self.current_return_type is None:
            # は？なんでいるん
            raise self._util_CallError("Globalでreturnはできません。しないでください", node.line, node.column, "", node.len)
        if node.value is None:
            if isinstance(self.current_return_type, TypeNone):
                return True
            return True
        rt = self._visit_expr_(node.value)
        if isinstance(rt, LiteralType):
            if self._can_literal_bind(rt, self.current_return_type):
                rt = self.current_return_type
        if rt == self.current_return_type:
            return True
        raise self._util_CallError(f"型が合致しません。期待する型{self.current_return_type},実際の型{rt}", node.line, node.column, "", node.len)
    
    def _visit_Declaration(self, node:DeclarationNode):
        # rightを検知してそのあと右との型整合性をはかる
        # Dynamicだったら右をそのまま使う
        if node.right is None:
            ntype = self._util_Typenode2type(node.type)
            if node.symbol is None:
                raise
            if isinstance(ntype, TypeDynamic):
                raise self._util_CallError("型推論が不完全です。", node.line, node.column, "", node.len)
            node.symbol.Type_analysis = ntype
            # 任務完了
            return False
        right = self._visit_expr_(node.right)
        ntype = self._util_Typenode2type(node.type)
        # リテラルと確定型の型合わせ
        # 右がLiteral、左が確定型
        if isinstance(right, LiteralType) and not isinstance(ntype, LiteralType):
            if self._can_literal_bind(right, ntype):
                right = ntype
        
        if isinstance(ntype, TypeDynamic):
            if isinstance(right, LiteralType):
                match (right):
                    case LiteralContainerType():
                        self._util_CallWarn("型推論が失敗しました。Listとして処理します。", node.line, node.column, "", node.len)
                        right = TypeList(right.Generic)
                    case LiteralDecimalType():
                        self._util_CallWarn("型推論が失敗しました。Float32として処理します。", node.line, node.column, "", node.len)
                        right = TypeFloat(32, False)
                    case LiteralNumberType():
                        self._util_CallWarn("型推論が失敗しました。Int32として処理します。", node.line, node.column, "", node.len)
                        right = TypeInt(32, False, True)
                    case LiteralStringType():
                        self._util_CallWarn("型推論が失敗しました。Stringとして処理します。", node.line, node.column, "", node.len)
                        right = TypeString()
                    case _:
                        raise self._util_CallError("型推論が失敗しました。", node.line, node.column, "", node.len)
            ntype = right
        # 型を出す
        if not right == ntype:
            self._util_CallError(f"型が一致しません！{ntype}と{right}", node.line, node.column, "binary", node.len)
        # ここで結果を格納
        if node.symbol is None:
            raise            
        # 設定
        node.symbol.Type_analysis = right
        # 任務完了
        return False
    
    def _visit_expr_can_change(self, node:Expr) -> TypeObject:
        # 可変か
        # じっしつらっぱ
        if not isinstance(node, (VariableNode, MemberAccessNode, IndexAccessNode, UnaryOpNode)):
            self._util_CallError(
                "This expression must be a modifiable expression",
                node.line,
                node.column,
                "_visit_expr_can_change",
                node.len
            )
            raise
        if isinstance(node, UnaryOpNode):
            if not node.op.type in (TokenType.MULT, TokenType.ADD):
                self._util_CallError(
                    "This expression must be a modifiable expression",
                    node.line,
                    node.column,
                    "_visit_expr_can_change",
                    node.len
                )
                raise
        return self._visit_expr_(node)
    
    def _visit_expr_(self, node:Optional[Expr]) -> TypeObject:
        if node is None:
            return TypeNone()
        match(node):
            case BinaryOpNode():
                # 実装終わった
                return self._visit_expr_binary(node)
            case Literal():
                # 実装終わった
                return self._visit_expr_literal(node)
            case UnaryOpNode():
                # おへ
                return self._visit_expr_Unary(node)
            case AssignNode():
                # ぽえ
                # TODO:_visit_expr_can_changeを実行して変更可能かを検知
                # TODO: Literal系と合致するかを決めてくださいな
                return self._visit_expr_assign(node)
            case CallExprNode():
                # ぽけ
                return self._visit_expr_CallExpr(node)
            case MemberAccessNode():
                # かれ
                # これはたぶん無理
                return self._visit_expr_Member(node)
            case IndexAccessNode():
                # なへり
                # インデックス元のGenelicをかえす
                return self._visit_expr_Index(node)
            case AsCastNode():
                # ぱら
                return self._visit_expr_AsCast(node)
            case MoveOpNode():
                return self._visit_expr_MoveOp(node)
            case BorrowOpNode():
                return self._visit_expr_BorrowOp(node)
            case _:
                raise
        
    def _visit_expr_MoveOp(self, node:MoveOpNode) -> TypeObject:
        to = self._visit_expr_(node.right)
        return to
    
    def _visit_expr_BorrowOp(self, node:BorrowOpNode) -> TypeObject:
        to = self._visit_expr_(node.right)
        to = TypeBorrow(to)
        return to
    
    def _visit_expr_Member(self, node:MemberAccessNode) -> TypeObject:
        if node.symbol is None:
            raise self._util_CallError("Member symbol not resolved", node.line, node.column, "", node.len)
        if node.symbol.Type_analysis is None:
            raise self._util_CallError("Member type not analyzed", node.line, node.column, "", node.len)
        return node.symbol.Type_analysis
    
    def _visit_expr_Index(self, node:IndexAccessNode) -> TypeObject:
        res = self._visit_expr_CallExpr_InSide(node.addr)
        # map[key, item]
        match (res):
            # ジェネリックを取得してindexが同じか
            # TypeList TypePtr TypeArray TypeMap
            case TypeList():
                index = self._visit_expr_(node.index)
                if not isinstance(index, TypeInt | LiteralNumberType):
                    raise
                return res.Generic
            case TypePtr():
                return res.Generic
            case TypeArray():
                index = self._visit_expr_(node.index)
                if not isinstance(index, TypeInt | LiteralNumberType):
                    raise
                # foo Array<int, 4>
                return res.Generic
            case TypeMap():
                key = self._visit_expr_(node.index)
                if not isinstance(key, type(res.key)):
                    raise
                return res.value
            case _:
                raise self._util_CallError("不明な不明", 0,0,"うはおｈさふぃおｓｆ",0)
    
    def _visit_expr_AsCast(self, node:AsCastNode) -> TypeObject:
        from_type = self._visit_expr_(node.obj)
        to_type = self._util_Typenode2type(node.type)

        if not self._can_cast(from_type, to_type, node.line, node.column, node.len):
            raise AnalysisError(f"Cannot cast {from_type} to {to_type}", node.line, node.column, self.source, "", node.len)

        return to_type
    
    def _can_cast(self, from_type: TypeObject, to_type: TypeObject, line:int, colum:int, len:int) -> bool:
        # 同型ならOK
        if from_type == to_type:
            return True
    
        # 整数系キャスト
        if isinstance(from_type, TypeInt) and isinstance(to_type, TypeInt):
            self._util_CallWarn(f"Casting {from_type} to {to_type} may lose data", line, colum, "", len)
            return True  # signed/unsigned や bit数は要方針
    
        # 整数→浮動小数点はOK
        if isinstance(from_type, TypeInt) and isinstance(to_type, TypeFloat):
            return True
    
        # 浮動小数点→整数はNG（強い型安全）
        if isinstance(from_type, TypeFloat) and isinstance(to_type, TypeInt):
            return False
    
        # それ以外はNG
        return False

    def _visit_expr_assign(self, node:AssignNode) -> TypeObject:
        # 変更可能か
        lt = self._visit_expr_can_change(node.left)
        # 結果(literal可能性あり)
        rt = self._visit_expr_(node.right)
        if isinstance(rt, LiteralType):
            if self._can_literal_bind(rt, lt):
                rt = lt
        if lt != rt:
            raise self._util_CallError(f"型:{rt}からは型:{lt}に代入ができません", node.line, node.column, "", node.len)
        return rt
    
    def _visit_expr_CallExpr(self, node:CallExprNode) -> TypeObject:
        """
        TODO: 関数呼び出しを実装する
        TODO: Exprを解析してその型を返す
        TODO: Argが合致しているか
        """
        ft = self._visit_expr_CallExpr_InSide(node.func_name)
        # (*foo)()
        if not isinstance(ft, TypeFunction):
            raise self._util_CallError("関数呼び出しには関数オブジェクトである必要があります。", node.line, node.column, "", node.len)
        for i,d in enumerate(node.args):
            t = self._visit_expr_(d)
            if isinstance(t, LiteralType):
                if self._can_literal_bind(t, ft.params[i]):
                    t = ft.params[i]
            if t != ft.params[i]:
                raise self._util_CallError("型が合致しません。", d.line, d.column, "", d.len)
        return ft.retype
    def _visit_expr_CallExpr_InSide(self, node:Expr) -> TypeObject:
        match (node):
            case AssignNode():
                # 右を返す
                return self._visit_expr_CallExpr_InSide(node.right)
            case UnaryOpNode():
                return self._visit_expr_CallExpr_InSide(node.right)
            case VariableNode():
                if node.symbol is None:
                    raise self._util_CallError(f"Symbolデータがありません。不明'{node.name}'", node.line, node.column, "", node.len)
                if node.symbol.Type_analysis is None:
                    raise
                return node.symbol.Type_analysis
            case MemberAccessNode():
                # bar.foo()
                # 1.add()
                if node.symbol is None:
                    # もし "左" もないなら？
                    # 意味わからん
                    # もはや新選組
                    # 右を撃ち値
                    tp = self._visit_expr_(node.left)
                    # 凶器のSATA
                    # バイナリーっぽく(stdclass参照)
                    ss = self.std.stdclass.make_std_class(tp)
                    if ss is None:
                        raise self._util_CallError(f"不明な型 '{ss}' 不明なメソッド呼び出し不可。", node.line, node.column, "", node.len)
                    # 神
                    ssn = [sym.name for sym in ss]
                    if node.right.name in ssn:
                        # お前を、、、、殺す！！
                        tssn = ss[ssn.index(node.right.name)].Type_analysis
                        if tssn is None:
                            raise self._util_CallError("不明なエラー。stdが破損しています", node.line, node.column, "", node.len)
                        return tssn
                    raise self._util_CallError(f"Symbolデータがありません。不明'{node.right.name}'", node.line, node.column, "", node.len)
                if node.symbol.Type_analysis is None:
                    raise
                return node.symbol.Type_analysis
            case IndexAccessNode():
                # foo[1] -> function
                # foo["as"]
                # [1] -> node.index
                # foo -> list[function...]
                res = self._visit_expr_CallExpr_InSide(node.addr)
                # map[key, item]
                match (res):
                    # ジェネリックを取得してindexが同じか
                    # TypeList TypePtr TypeArray TypeMap
                    case TypeList():
                        index = self._visit_expr_(node.index)
                        if not isinstance(index, TypeInt | LiteralNumberType):
                            raise
                        return res.Generic
                    case TypePtr():
                        return res.Generic
                    case TypeArray():
                        index = self._visit_expr_(node.index)
                        if not isinstance(index, TypeInt | LiteralNumberType):
                            raise
                        # foo Array<int, 4>
                        return res.Generic
                    case TypeMap():
                        key = self._visit_expr_(node.index)
                        if not isinstance(key, type(res.key)):
                            raise
                        return res.value
                    case _:
                        raise self._util_CallError("不明な式", node.line, node.column, "", node.len)
            case MoveOpNode():
                return self._visit_expr_CallExpr_InSide(node.right)
            case BorrowOpNode():
                return TypeBorrow(self._visit_expr_CallExpr_InSide(node.right))
            case _:
                raise self._util_CallError("不明な呼び出し\n不明な式は関数呼び出しでは使用ができません。", node.line, node.column, "", node.len)

    def _visit_expr_Unary(self, node:UnaryOpNode) -> TypeObject:
        """
        単項演算子
        2項演算子っぽく実装
        TODO: コピペ実装する
        """
        
        # アウトな奴
        ProhibitedScheme:dict[TokenType, list[type[TypeObject]]] = {
            TokenType.ADD:[],
            TokenType.PLUS:[TypeArray, TypeList, TypeBool, TypeFunction, TypeString],
            TokenType.MINUS:[TypeArray, TypeList, TypeBool, TypeFunction, TypeString],
        }

        # 結果の型。
        TypeScheme:dict[TokenType, TypeObject] = {
            TokenType.ADD:TypePtr(TypeTemplate(1)),
            TokenType.PLUS:TypeTemplate(1),
            TokenType.MINUS:TypeTemplate(1),
        }
        # 型のget
        right = self._visit_expr_(node.right)
        prohib = ProhibitedScheme[node.op.type]
        # 明らかアウト
        if type(right) in prohib:
            raise self._util_CallError(f"Op {node.op.String}", node.line, node.column, "BinaryOp", node.len)
        
        # 型を出す
        scheme = TypeScheme[node.op.type]
        return self._util_TemplateReptile(scheme, right)
    
    def _visit_expr_literal(self, node:Literal) -> TypeObject:
        """
        NumberNode
        VariableNode
        FunctionNode
        StringNode
        NullNode
        NoneNode
        BoolNode
        """
        match(node):
            case NumberNode():
                return LiteralNumberType()
            case VariableNode():
                # TODO: symbolアクセス
                if node.symbol is None:
                    raise
                if node.symbol.Type_analysis is None:
                    raise self._util_CallError("型が未決定です。前方宣言または正しい位置での宣言が必要です", node.line, node.column, "", node.len)
                return node.symbol.Type_analysis
            case StringNode():
                return LiteralStringType()
            case NullNode():
                return TypeNull()
            case NoneNode():
                return TypeNone()
            case BoolNode():
                return TypeBool()
            case DecimalNode():
                return LiteralDecimalType()
            case _:
                # TODO: だとおもった？
                raise


    def _visit_expr_binary(self, node:BinaryOpNode) -> TypeObject:
        # アウトな奴
        ProhibitedScheme:dict[TokenType, list[type[TypeObject]]] = {
            TokenType.PLUS:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.MINUS:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.MULT:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.DIV:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.DOUBLEDOT:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone, TypeFloat, ],
            TokenType.EQ:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.NE:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.LE:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
            TokenType.GE:[TypeFunction, TypeString, MiddleTypeObject, TypeNull, TypeNone],
        }

        # 結果の型。
        TypeScheme:dict[TokenType, TypeObject] = {
            TokenType.PLUS:TypeTemplate(1),
            TokenType.MINUS:TypeTemplate(1),
            TokenType.MULT:TypeTemplate(1),
            TokenType.DIV:TypeTemplate(1),
            TokenType.DOUBLEDOT:LiteralContainerType(TypeTemplate(1)),
            TokenType.EQ:TypeBool(),
            TokenType.NE:TypeBool(),
            TokenType.LE:TypeBool(),
            TokenType.GE:TypeBool(),
        }
        # 型のget
        right = self._visit_expr_(node.right)
        left = self._visit_expr_(node.left)
        prohib = ProhibitedScheme[node.op.type]
        # 明らかアウト
        if isinstance(right, (*prohib,)) or isinstance(left, (*prohib,)):
            raise self._util_CallError(f"Op {node.op.String}", node.line, node.column, "BinaryOp", node.len)
        
        # もしもし「しもしも」
        if isinstance(left, LiteralType) and isinstance(right, LiteralType):
            if type(left) != type(right):
                if isinstance(left, LiteralDecimalType) or isinstance(right, LiteralDecimalType):
                    left = right = LiteralDecimalType() 

        # リテラルと確定型の型合わせ
        # 左がLiteral、右が確定型
        if isinstance(left, LiteralType) and not isinstance(right, LiteralType):
            if self._can_literal_bind(left, right):
                left = right
        # 右がLiteral、左が確定型
        elif isinstance(right, LiteralType) and not isinstance(left, LiteralType):
            if self._can_literal_bind(right, left):
                right = left
        # 型を出す
        scheme = TypeScheme[node.op.type]
        if not right == left:
            self._util_CallError(f"型が合いません！右:{left}左:{right}", node.line, node.column, "binary", node.len)
        return self._util_TemplateReptile(scheme, right)

    def _util_TemplateReptile(self, type:TypeObject, temp:TypeObject) -> TypeObject:
        # ここ
        match (type):
            case TypeList():
                return TypeList(self._util_TemplateReptile(type.Generic, temp))
            case TypePtr():
                return TypePtr(self._util_TemplateReptile(type.Generic, temp))
            case TypeArray():
                return TypeArray(self._util_TemplateReptile(type.Generic, temp), type.len)
            case LiteralContainerType():
                return LiteralContainerType(self._util_TemplateReptile(type.Generic, temp))
            case TypeBorrow():
                return TypeBorrow(self._util_TemplateReptile(type.Generic, temp))
            case TypeTemplate():
                return temp
            case _:
                return type

    
    def _can_literal_bind(self, literal: LiteralType, target: TypeObject) -> bool:
        """リテラルがターゲットの型に化けられるか判定する"""
        if isinstance(literal, LiteralNumberType):
            if isinstance(target, TypeFloat) or isinstance(target, LiteralDecimalType):
                return True
            else:
                return isinstance(target, TypeInt) # すべての整数系
        if isinstance(literal, LiteralDecimalType):
            return isinstance(target, TypeFloat)
        if isinstance(literal, LiteralStringType):
            return isinstance(target, TypeString)
        return False

# 借用チェック
class BorrowingChecker:
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.source = source
        self.borrow_ledger_stack: list[list[dict[Symbol, list[Symbol]]]] = []
    
    def new_Frame(self) -> None:
        self.borrow_ledger_stack.append([])
        return
    
    def pop_Frame(self) -> list[dict[Symbol, list[Symbol]]] | None:
        if len(self.borrow_ledger_stack) == 0:
            return None
        res = self.borrow_ledger_stack.pop()
        return res
    
    def get_Frame(self) -> list[dict[Symbol, list[Symbol]]] | None:
        if len(self.borrow_ledger_stack) == 0:
            return None
        res = self.borrow_ledger_stack[-1]
        return res
    
    def _util_CallError(self, message: str, line: int, column: int, name: str, len: int) -> AnalysisError:
        raise AnalysisError(message, line, column, self.source, name, len)

    def _util_CallWarn(self, message: str, line: int, column: int, name: str, len: int) -> None:
        print("警告" + AnalysisError(message, line, column, self.source, name, len).__str__())
    
    def visit_BorrowingChecker(self):
        return self._visit_Program(self.node)
    
    def _visit_Program(self, node:Program):
        for i in node.blocks:
            self._visit_Stmt(i)
        return

    def _visit_Stmt(self, node:Stmt):
        """
class DeclarationNode(Stmt):
class ExprStmtNode(Stmt):
class BlockNode(Stmt):
class IfStmtNode(Stmt):
class WhileStmtNode(Stmt):
class FunctionDefNode(Stmt):
class ReturnStmtNode(Stmt):
class ClassDefNode(Stmt):
class Program(Stmt):
class ForNode(Stmt):
class ImportNode(Stmt):
        """
        match (node):
            case DeclarationNode():
                return self._visit_Declaration(node)
            case ExprStmtNode():
                return self._visit_ExprStmt(node)
            case BlockNode():
                return self._visit_Block(node)
            case IfStmtNode():
                return self._visit_IfStmt(node)
            case WhileStmtNode():
                return self._visit_WhileStmt(node)
            case FunctionDefNode():
                return self._visit_FunctionDef(node)
            case ReturnStmtNode():
                return self._visit_ReturnStmt(node)
            case ForNode():
                return self._visit_ForStmt(node)
            case ImportNode():
                return self._visit_Import(node)
            case _:
                raise self._util_CallError(f"不明なnode '{node}'", node.line, node.column, "", node.len)

    def _visit_Declaration(self, node:DeclarationNode):
        # 終わってる
        return
    def _visit_expr(self, node:Expr) -> AnalysisBorrow | None:
        match (node):
            case VariableNode():
                if node.symbol is None:
                    raise self._util_CallError("symbolデータが未定義です", node.line, node.column, "", node.len)
                # MOVEDなら死
                if node.symbol.borrow_state == Borrow.MOVED:
                    raise self._util_CallError(f"変数'{node.name}'は移動されています。", node.line, node.column, "", node.len)
                if node.symbol.borrow_state == Borrow.NONE:
                    raise self._util_CallError(f"変数'{node.name}'は不明な状態です。使用はできません", node.line, node.column, "", node.len)
                return AnalysisBorrow(node.symbol.borrow_state, node.symbol)
            case AssignNode():
                # 禿げろ
                lab = self._visit_expr_can_change(node.left)
                rab = self._visit_expr(node.right)
                lb = lab.borrow
                if lb == Borrow.BORROW:
                    raise self._util_CallError(f"変数'{}'は変数'{}'から型:{}のオブジェクトを借りています。")
                if lb == Borrow.BORROWED:
                    raise self._util_CallError(f"変数'{}'は変数'{}'に型:{}のオブジェクトを借りられています。")
                if not rab is None:
                    rb = rab.borrow
                    if rb == Borrow.UNINIT:
                        raise self._util_CallError(f"変数'{}'は内容が入らない可能性があるため代入は不可能です。")
                    if rab.from_.Type_analysis is None:
                        raise
                    # 神
                    
                
                return AnalysisBorrow(Borrow.ACTIVE, lab.from_)
            case _:
                raise self._util_CallError("なんですか、、、", node.line, node.column, "", node.len)
    
    def _visit_expr_can_change(self, node:Expr) -> AnalysisBorrow:
        if not isinstance(node, (VariableNode, MemberAccessNode, IndexAccessNode, UnaryOpNode)):
            self._util_CallError(
                "変更不可なオブジェクト。",
                node.line,
                node.column,
                "_visit_expr_can_change",
                node.len
            )
            raise
        if isinstance(node, UnaryOpNode):
            if not node.op.type in (TokenType.MULT, TokenType.ADD):
                self._util_CallError(
                    "",
                    node.line,
                    node.column,
                    "_visit_expr_can_change",
                    node.len
                )
                raise
        res = self._visit_expr(node)
        # res is none
        if res is None:
            raise self._util_CallError("不明なエラー。", node.line, node.column, "", node.len)
        return res


if __name__ == "__main__":
    t = BinaryOpNode(0,0,0,NumberNode(0,0,0,42,Token(TokenType.NUMBER, 42),10),Token(TokenType.DOUBLEDOT, "+"), NumberNode(0,0,0,42,Token(TokenType.NUMBER, 42),10))
    tc = TypeChecker(Program(0,0,0,[]),"")
    print(tc._visit_expr_binary(t))