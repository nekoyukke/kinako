from typing import Callable

from src.frontend.lexer.token import Token
from src.frontend.lexer.tokentype import TokenType
import src.core.ast.base as _base
import src.core.ast.expr as _expr
import src.core.ast.stmt as _stmt
from src.utils.error.syntax import KinakoSyntaxError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo, KinakoBaseError

class Parser():
    def __init__(self, tokens:list[Token], source:str) -> None:
        self.tokens: list[Token] = tokens
        self.source: str = source
        self.pos = 0
        self.error: list[KinakoBaseError] = []
        self.indent: int = 0
    
    def peek(self) -> Token:
        """現在のトークンを覗き見る"""
        return self.tokens[self.pos]

    def is_at_end(self) -> bool:
        """最後まで行ったか"""
        return self.peek().type == TokenType.EOF

    def advance(self) -> Token:
        """一つ進めて、進める前のトークンを返す"""
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def previous(self) -> Token:
        """一つ前のトークン"""
        return self.tokens[self.pos - 1]

    def check(self, type: TokenType) -> bool:
        """型が一致するか確認(消費しない)"""
        if self.is_at_end():
            return False
        return self.peek().type == type

    def match(self, *types: TokenType) -> bool:
        """型が一致すれば消費してTrue"""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False
    
    def accept(self, *types: TokenType) -> Token | None:
        """型が一致すれば消費してそれ自身を返し、そうでなければNoneを返す"""
        for t in types:
            if self.check(t):
                res = self.advance()
                return res 
        return

    def consume(self, type: TokenType, message: str) -> Token:
        """期待した型なら消費、違えばError"""
        if self.check(type):
            return self.advance()
        current = self.peek()
        self.CallError(message, _base.ASTNode(current.line, current.column, current.len))
    
    def CallError(
            self, message:str ,node:_base.ASTNode,
            related: list[KinakoRelatedInfo] | None = None,
            help: list[KinakoHelp] | None = None
        ):
        """
        エラー呼び出し
        """
        err =  KinakoSyntaxError(
            message,
            node.line,
            node.col,
            self.source,
            node.len,
            related,
            help
        )
        self.error.append(err)
        raise err


    def synchronize(self):
        tok = self.advance()

        if tok.type == TokenType.LBRACE:
            while not self.peek().type == TokenType.RBRACE:
                self.advance()
            self.advance()
            print(self.peek())
            return

        while not self.is_at_end():
            # セミコロンの直後なら、次の文から再開できる可能性が高い
            if self.previous().type == TokenType.SEMI:
                print(self.peek())
                return

            # 次の文の開始キーワードを見つけたら、そこで同期
            if self.peek().type in {
                TokenType.FN, TokenType.IF, 
                TokenType.FOR, TokenType.WHILE, TokenType.RETURN
            }:
                print(self.peek())
                return

            self.advance()

    def parse(self):
        return self._Program()
    
    def _Program(self) -> _stmt.ProgramStmt:
        stmts: list[_stmt.Stmt] = []
        while not self.is_at_end():
            stmt = self._Stmt_entry()
            if stmt is None:
                continue
            stmts.append(stmt)
            continue
        return _stmt.ProgramStmt(0,0,0, stmts)
    
    def _Stmt_entry(self) -> None | _stmt.Stmt:
        try:
            return self._Stmt()
        except KinakoSyntaxError: 
            self.synchronize()
        return
    

    def _Stmt(self) -> _stmt.Stmt:
        match(self.peek().type):
            case TokenType.LET:
               return self.let_node()
            case TokenType.FN:
                return self.fndefine_node()
            case TokenType.FOR:
                return self.for_node()
            case TokenType.WHILE:
                return self.while_node()
            case TokenType.IF:
                return self.if_node()
            case TokenType.RETURN:
                return self.return_node()
            case TokenType.LBRACE:
                return self.block_node()
            case _:
                expr = self._expr_entry()
                self.consume(TokenType.SEMI, "セミコロンがありません！")
                return _stmt.ExprStmt(expr.line, expr.col, expr.len, expr)
    # A | B[C]なら
    # Union(A, Generic(B, C))
    def get_Union_identifier(self, message:str) -> _base.Identifier:
        ident = self.get_generic_identifier(message)
        if not self.check(TokenType.UNION):
            return ident
        result = _base.Union_Identifier([ident])
        while self.match(TokenType.UNION):
            result.identifiers.append(self.get_generic_identifier(message))
        return result
    
    def get_generic_identifier(self, message:str) -> _base.Identifier:
        ident = self.get_real_identifier(message)
        if not self.match(TokenType.LBRACKET):
            return ident
        ident_generic = self.get_Union_identifier(message)
        self.consume(TokenType.RBRACKET, message)
        return _base.Generic_Identifier(ident_generic, ident)
    
    def get_real_identifier(self, message:str) -> _base.Identifier:
        tok = self.consume(TokenType.ID, message)
        return _base.Real_Identifier(tok.value)

    def get_variable(self, message:str) -> _expr.Variable:
        result = self.consume(TokenType.ID, message)
        return _expr.Variable(result.line, result.column, result.len, None, result.value)

    def get_contract(self, message:str) -> _base.Contract:
        type = self.get_Union_identifier(f"型パース失敗！{message}")
        right = self.get_Union_identifier(f"権利パース失敗！{message}")
        policy = self.get_Union_identifier(f"制約パース失敗！{message}")
        return _base.Contract(type, right, policy)
    
    def if_node(self) -> _stmt.Ifstmt:
        iftok = self.advance()
        
        # 条件と実行文
        condition = self._expr_entry()
        then_stmt = self._Stmt()
        
        else_stmt: _stmt.Stmt | None = None

        if self.peek().type == TokenType.ELIF:
            # elif を「if」として再帰的にパースする
            else_stmt = self.if_node_Elif_helper()
        elif self.peek().type == TokenType.ELSE:
            self.advance()
            else_stmt = self._Stmt()
            
        return _stmt.Ifstmt(iftok.line, iftok.column, iftok.len, condition, then_stmt, else_stmt)

    def if_node_Elif_helper(self) -> _stmt.Ifstmt:
        # elif トークンを消費して、中身は if と同じように処理
        iftok = self.advance()
        condition = self._expr_entry()
        then_stmt = self._Stmt()
        
        else_stmt = None
        if self.peek().type == TokenType.ELIF:
            else_stmt = self.if_node_Elif_helper() # さらに続くなら再帰
        elif self.peek().type == TokenType.ELSE:
            self.advance()
            else_stmt = self._Stmt()
            
        return _stmt.Ifstmt(iftok.line, iftok.column, iftok.len, condition, then_stmt, else_stmt)
    
    def for_node(self) -> _stmt.ForEachStmt:
        fortok = self.advance()
        
        var = self.get_variable("forでは識別子が必要です")
        contract = _base.Contract(None, None, None)
        if self.match(TokenType.COLON):
            contract = self.get_contract("forでは、コントラクトが必要です。")
        
        # INキーワードのチェック
        self.consume(TokenType.IN, "反復変数の後にはinが必要です。")
        
        # 繰り返す対象の式
        expr = self._expr_entry()
        
        body = self._Stmt()
        return _stmt.ForEachStmt(fortok.line, fortok.column, fortok.len, expr, var, contract, body)
    
    def while_node(self) -> _stmt.WhileStmt:
        while_token = self.advance()
        condition = self._expr_entry()
        body = self._Stmt()
        return _stmt.WhileStmt(while_token.line, while_token.column, while_token.len, condition, body)
    
    def return_node(self):
        return_token = self.advance()
        expr = self._expr_entry()
        self.consume(TokenType.SEMI, "セミコロンがありません")
        return _stmt.ReturnStmt(
            return_token.line,
            return_token.column,
            return_token.len,
            expr
        )
        
    def fndefine_node(self):
        define_token = self.advance()
        id_token = self.consume(TokenType.ID, "識別子がありません。")
        self.consume(TokenType.LPAREN, "かっこ '(' がありません")
        args:list[_base.Parameter] = []
        if self.peek().type != TokenType.RPAREN:
            while True:
                id_str = self.consume(TokenType.ID, "識別子が必要です。").value
                contract_arg = _base.Contract(None, None, None)
                if self.match(TokenType.COLON):
                    contract_arg = self.get_contract("宣言式")
                args.append(_base.Parameter(id_str, contract_arg))
                if self.peek().type == TokenType.COMMA:
                    self.advance()
                    continue
                break
        self.consume(TokenType.RPAREN, "かっこ ')' がありません")
        contract = _base.Contract(None, None, None)
        if self.match(TokenType.ARROW):
            contract = self.get_contract("関数定義には必須です！！")
        body = self._Stmt_entry()
        if body is None:
            self.CallError("不明な構文。正しくはfn <name>(args) -> contract {...}", _expr.Variable(
                define_token.line, define_token.column, define_token.len, None,
                define_token.value))
            
        return _stmt.FunctionDeclStmt(
                define_token.line,
                define_token.column,
                define_token.len,
                _expr.Variable(id_token.line, id_token.column, id_token.len, None, id_token.value),
                contract,
                args,
                body,
            )
    
    def block_node(self):
        token = self.advance()
        self.indent += 1
        stmts: list[_stmt.Stmt] = []
        while (not self.is_at_end()) and self.peek().type != TokenType.RBRACE:
            stmt = self._Stmt_entry()
            if stmt is None:  # type: ignore
                continue
            stmts.append(stmt)
        self.consume(TokenType.RBRACE, "blockが閉じられていません。")
        self.indent -= 1
        return _stmt.BlockStmt(token.line, token.column, token.len, stmts)
    
    def let_node(self):
        current = self.advance()
        variable = self.get_variable("宣言では識別子が必須です。")
        contract = _base.Contract(None, None, None)
        if self.match(TokenType.COLON):
            contract = self.get_contract("宣言ではコントラクト宣言が必須です")
        if self.peek().type == TokenType.SEMI:
            self.consume(TokenType.SEMI, "セミコロンがありません！")
            return _stmt.VariableDeclStmt(current.line, current.column, current.len, variable, contract, None)
        self.consume(TokenType.ASSIGN, "'='がないです。代入が完成しません")
        expr = self._expr_entry()
        self.consume(TokenType.SEMI, "セミコロンがありません！")
        return _stmt.VariableDeclStmt(current.line, current.column, current.len, variable, contract, expr)







# point nemo!! <- Good!!







    def left_binary_op(
            self, next_func: Callable[[], _expr.Expr], token_types: dict[TokenType, _expr.kinds],
            node_factory: Callable[[_expr.kinds, _expr.Expr, _expr.Expr], _expr.Expr]
            ) -> _expr.Expr:
        node = next_func() 

        while self.peek().type in token_types:
            operator_token = self.advance()

            right = next_func()

            # 左結合
            node = node_factory(token_types[operator_token.type], node, right)
        
        return node
    
    def right_binary_op(
            self, next_func: Callable[[], _expr.Expr], token_types: dict[TokenType, _expr.kinds],
            node_factory: Callable[[_expr.kinds, _expr.Expr, _expr.Expr], _expr.Expr]
            ) -> _expr.Expr:
        node = next_func()
        
        if self.peek().type in token_types:
            operator_token = self.advance()
            right = self.right_binary_op(next_func, token_types, node_factory)
            node = node_factory(token_types[operator_token.type], node, right)
        return node
    

    def _make_binary(self, kind: _expr.kinds, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """算術演算・比較演算用の工場"""
        if not isinstance(kind, _expr.BinaryKind):
            self.CallError(
                f"不明な演算子エラー。_expr.kindsが不十分です。\nデバッグ情報:kind:{kind}, left:{left}, right:{right}",
                left,
                help=[KinakoHelp("コンパイラエラー")]
            )
        return _expr.BinaryExpr(
            line=left.line,
            col=left.col,
            len=left.len,
            op=kind,
            left=left,
            right=right,
            id=None
        )

    def _make_logical(self, kind: _expr.kinds, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """&& や || などの論理演算用の工場"""
        if not isinstance(kind, _expr.LogicKind):
            self.CallError(
                f"不明な演算子エラー。_expr.kindsが不十分です。\nデバッグ情報:kind:{kind}, left:{left}, right:{right}",
                left,
                help=[KinakoHelp("コンパイラエラー")]
            )
        return _expr.LogicExpr(
            line=left.line,
            col=left.col,
            len=left.len,
            op=kind,
            left=left,
            right=right,
            id=None
        )

    def _make_assign(self, kind: _expr.kinds, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """代入用の工場"""
        if not isinstance(kind, _expr.AssignKind):
            self.CallError(
                f"不明な演算子エラー。_expr.kindsが不十分です。\nデバッグ情報:kind:{kind}, left:{left}, right:{right}",
                left,
                help=[KinakoHelp("コンパイラエラー")]
            )
        return _expr.AssignExpr(
            line=left.line,
            col=left.col,
            len=left.len,
            op=kind,
            left=left,
            right=right,
            id=None
        )


    def _expr_entry(self) -> _expr.Expr:
        return self.assignment()
    
    def assignment(self) -> _expr.Expr:
        return self.right_binary_op(self.logical_or, 
            {
                TokenType.ASSIGN:_expr.AssignKind.ASSIGN,
            },
            self._make_assign
        )

    def logical_or(self) -> _expr.Expr:
        return self.left_binary_op(
            self.logical_and,
            {TokenType.LOGIC_OR:_expr.BinaryKind.LOGIC_OR},
            self._make_logical
        )

    def logical_and(self) -> _expr.Expr:
        return self.left_binary_op(self.equality, {TokenType.LOGIC_AND:_expr.BinaryKind.LOGIC_AND}, self._make_logical)

    def equality(self) -> _expr.Expr:
        return self.left_binary_op(self.comparison, {TokenType.EQ:_expr.LogicKind.EQ, TokenType.NE:_expr.LogicKind.NE}, self._make_binary)

    def comparison(self) -> _expr.Expr:
        return self.left_binary_op(self.term, {
            TokenType.LABRACKET: _expr.LogicKind.LT,
            TokenType.GE: _expr.LogicKind.GE,
            TokenType.RABRACKET: _expr.LogicKind.GT,
            TokenType.LE: _expr.LogicKind.LE
        }, self._make_binary)

    def term(self) -> _expr.Expr:
        return self.left_binary_op(self.factor, {TokenType.PLUS:_expr.BinaryKind.PLUS, TokenType.MINUS:_expr.BinaryKind.MINUS}, self._make_binary)

    def factor(self) -> _expr.Expr:
        return self.left_binary_op(self.prefix, {TokenType.MULT:_expr.BinaryKind.MULT, TokenType.DIV:_expr.BinaryKind.DIV}, self._make_binary)
    
    def prefix(self) -> _expr.Expr:
        # prefix (前置演算)
        if self.match(TokenType.MINUS, TokenType.PLUS):
            operator_token = self.previous()
            right = self.prefix() # 自分自身を再帰的に呼ぶ
            return _expr.UnaryExpr(
                operator_token.line, operator_token.column, operator_token.len, None,
                right, _expr.UnaryKind.MINUS if operator_token.type==TokenType.MINUS else _expr.UnaryKind.PLUS
            )
        
        return self.postfix()

    def postfix(self) -> _expr.Expr:
        # postfix (後置演算: 関数呼び出し、配列アクセス、プロパティ)
        node:_expr.Expr = self.primary()

        while True:
            if self.match(TokenType.LPAREN): # 関数呼び出し a()
                node = self._finish_call(node)
            elif self.match(TokenType.LBRACKET): # インデックス a[0]
                index = self._expr_entry()
                self.consume(TokenType.RBRACKET, "']'がありません。トークン不足！")
                node = _expr.IndexExpr(node.line, node.col, node.len, None, node, index)
            elif self.match(TokenType.DOT): # プロパティアクセス a.b
                name = self.get_variable("プロパティ名が必要です。")
                node = _expr.MemberExpr(node.line, node.col, node.len, None, node, name)
            else:
                break
        
        return node
    
    def primary(self) -> _expr.Expr:
        current = self.peek()
        note:list[KinakoHelp] = []
        match(current.type):
            case TokenType.NUMBER:
                self.advance()
                return _expr.IntLiteral(current.line, current.column, current.len, None, int(current.value))
            case TokenType.DECIMAL:
                self.advance()
                return _expr.FloatLiteral(current.line, current.column, current.len, None, float(current.value))
            case TokenType.ID:
                return self.get_variable("変数が必要です")
            case TokenType.LPAREN:
                self.advance()
                expr = self._expr_entry()
                self.consume(TokenType.RPAREN, "')'が閉じられていません！！")
                return expr
            case TokenType.STRING:
                self.advance()
                return _expr.StringLiteral(current.line, current.column, current.len, None, current.value)
            # ミスケース
            case TokenType.LET:
                note.append(
                    KinakoHelp(
                        "もしかしたら、宣言文が不完全ではありませんか？"
                    )
                )
                self.CallError(f"不明なトークン{current.value}。",
                               _base.ASTNode(current.line, current.column, current.len), [], note)
            case TokenType.LBRACE | TokenType.LABRACKET | TokenType.LBRACKET:
                note.append(
                    KinakoHelp(
                        "もしかしたら、意味を為さない不明な式/文ではありませんか？"
                    )
                )
                current = self.previous()
                self.CallError(f"不明なトークン{current.value}。",
                               _base.ASTNode(current.line, current.column, current.len), [], note)
            case _:
                self.CallError(f"不明なトークン{current.value}。",
                               _base.ASTNode(current.line, current.column, current.len), [], note)
    
    def _finish_call(self, expr:_expr.Expr) -> _expr.Expr:
        # 関数呼び出し
        func = self.previous()
        # a(1,2)
        #   ^
        args: list[_expr.Expr] = []
        while (self.peek().type != TokenType.RPAREN):
            op = self._expr_entry()
            args.append(op)
            if (self.peek().type == TokenType.COMMA):
                self.consume(TokenType.COMMA, "','がありません！！")
                continue
            else:
                break
        self.consume(TokenType.RPAREN,"')'がありません！")
        end = self.peek()
        return _expr.CallExpr(func.line, func.column, end.column - func.column, None, expr, args)