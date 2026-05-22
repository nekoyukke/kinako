from typing import Callable

from src.frontend.lexer.token import Token
from src.frontend.lexer.tokentype import TokenType, NOT_GEMERIC
import src.frontend.parser.models.stmt as _stmt
import src.frontend.parser.models.expr as _expr
import src.frontend.parser.models.literal as _literal
import src.frontend.parser.models.type as _type
from src.core.node.ast_base import ASTNode

from src.core.id_base.node_id import NodeId

from src.utils.error.base import KinakoRelatedInfo, KinakoHelp, KinakoBaseError
from src.utils.error.syntax import KinakoSyntaxError


from src.core.possession.possession import PossessionFlag, Possession

class Parser():
    TOKEN_TO_EFFECTS: dict[TokenType, PossessionFlag] = {
        TokenType.LET: PossessionFlag.COPYABLE | PossessionFlag.MOVABLE | PossessionFlag.MUTABLE | PossessionFlag.BORROWABLE,
        TokenType.MUT: PossessionFlag.MOVABLE | PossessionFlag.MUTABLE | PossessionFlag.BORROWABLE,
        TokenType.CONST: PossessionFlag.COPYABLE | PossessionFlag.MOVABLE | PossessionFlag.BORROWABLE,
    }

    def __init__(self, tokens: list[Token] ,source:str) -> None:
        self.tokens: list[Token] = tokens
        self.source: str = source
        self.pos = 0
        self.error: list[KinakoBaseError] = []
        self.id = 0
    
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

    def consume(self, type: TokenType, message: str) -> Token:
        """期待した型なら消費、違えばError"""
        if self.check(type):
            return self.advance()
        current = self.peek()
        self.CallError(message, ASTNode(current.line, current.column, current.len,  self.new_id(), None,))
    
    def new_id(self) -> NodeId:
        id = self.id
        self.id += 1
        return NodeId(id)
    
    def CallError(
            self, message:str ,node:ASTNode,
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
        self.advance()

        while not self.is_at_end():
            # セミコロンの直後なら、次の文から再開できる可能性が高い
            if self.previous().type == TokenType.SEMI:
                return

            # 次の文の開始キーワードを見つけたら、そこで同期
            if self.peek().type in {
                TokenType.FN, TokenType.LET, TokenType.IF, 
                TokenType.FOR, TokenType.WHILE, TokenType.RETURN
            }:
                return

            self.advance()

    def parse(self):
        return self._Program()
    
    def _Program(self) -> _stmt.Program:
        stmts: list[_stmt.Stmt] = []
        import_stmts: list[_stmt.ImportNode] = []
        while not self.is_at_end():
            stmt = self._Stmt_entry()
            if stmt is None:
                continue
            if isinstance(stmt, _stmt.ImportNode):
                import_stmts.append(stmt)
                continue
            stmts.append(stmt)
            continue
        return _stmt.Program(0,0,0,  self.new_id(), None,stmts, [], import_stmts)
    
    def _Stmt_entry(self) -> None | _stmt.Stmt | _stmt.ImportNode:
        try:
            return self._Stmt()
        except KinakoSyntaxError: 
            self.synchronize()
        return
    

    def _Stmt(self):
        match(self.peek().type):
            case TokenType.LET | TokenType.CONST | TokenType.MUT:
               return self.let_node_entry()
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
            case TokenType.IMPORT:
                return self.import_node()
            case TokenType.LBRACE:
                return self.block_node()
            case TokenType.ANCHOR:
                return self.anchor_node()
            case TokenType.HOLD:
                return self.hold_node()
            case TokenType.GRAB:
                return self.grab_node()
            case _:
                expr = self._expr_entry()
                self.consume(TokenType.SEMI, "セミコロンがありません！")
                return _stmt.ExprStmtNode(expr.line, expr.col, expr.len,  self.new_id(), None, expr)
    
    def grab_node(self) -> _stmt.GrabStmtNode:
        grab_tok = self.advance()
        id_token = self.consume(TokenType.ID, "'anchor'構文では識別子を入力する必要があります。")
        then_stmt = self._Stmt()
        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self._Stmt()
        return _stmt.GrabStmtNode(
            grab_tok.line, grab_tok.column, grab_tok.len,  self.new_id(), None,
            _expr.VariableNode(id_token.line, id_token.column, id_token.len,  self.new_id(), None, None, id_token.value),
            then_stmt,
            else_stmt
        )

    def hold_node(self) -> _stmt.HoldStmtNode:
        hold_tok = self.advance()
        id_token = self.consume(TokenType.ID, "'anchor'構文では識別子を入力する必要があります。")
        then_stmt = self._Stmt()
        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self._Stmt()
        return _stmt.HoldStmtNode(
            hold_tok.line, hold_tok.column, hold_tok.len,  self.new_id(), None,
            _expr.VariableNode(id_token.line, id_token.column, id_token.len,  self.new_id(), None, None, id_token.value),
            then_stmt,
            else_stmt
        )

    def anchor_node(self) -> _stmt.AnchorStmtNode:
        anchor_tok = self.advance()
        id_token = self.consume(TokenType.ID, "'anchor'構文では識別子を入力する必要があります。")
        then_stmt = self._Stmt()
        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self._Stmt()
        return _stmt.AnchorStmtNode(
            anchor_tok.line, anchor_tok.column, anchor_tok.len,  self.new_id(), None,
            _expr.VariableNode(id_token.line, id_token.column, id_token.len,  self.new_id(), None, None, id_token.value),
            then_stmt,
            else_stmt
        )

    def if_node(self) -> _stmt.IfStmtNode:
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
            
        return _stmt.IfStmtNode(iftok.line, iftok.column, iftok.len,  self.new_id(), None, condition, then_stmt, else_stmt)

    def if_node_Elif_helper(self) -> _stmt.IfStmtNode:
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
            
        return _stmt.IfStmtNode(iftok.line, iftok.column, iftok.len,  self.new_id(), None, condition, then_stmt, else_stmt)
    
    def for_node(self) -> _stmt.ForStmtNode:
        fortok = self.advance()
        
        var_tok = self.consume(TokenType.ID, "forでは識別子が必要です")
        var = _expr.VariableNode(var_tok.line, var_tok.column, var_tok.len,  self.new_id(), None, None, var_tok.value)
        
        # INキーワードのチェック
        self.consume(TokenType.IN, "反復変数の後にはinが必要です。")
        
        # 繰り返す対象の式
        expr = self._expr_entry()
        
        body = self._Stmt()
        return _stmt.ForStmtNode(fortok.line, fortok.column, fortok.len,  self.new_id(), None, var, expr, body)
    
    def while_node(self) -> _stmt.WhileStmtNode:
        while_token = self.advance()
        condition = self._expr_entry()
        body = self._Stmt()
        return _stmt.WhileStmtNode(while_token.line, while_token.column, while_token.len,  self.new_id(), None, condition, body)
    
    def import_node(self):
        import_token = self.peek()
        self.advance()
        expr_import = self.consume(TokenType.STRING, "不明なリテラル")
        self.consume(TokenType.SEMI, "セミコロンがありません。")
        return _stmt.ImportNode(
            import_token.line,
            import_token.column,
            import_token.len,
             self.new_id(), None,
            _literal.StrLiteralNode(
                expr_import.line,
                expr_import.column,
                expr_import.len,
                 self.new_id(), None,
                None,
                expr_import.value
            )
        )
    
    def return_node(self):
        return_token = self.advance()
        expr = self._expr_entry()
        self.consume(TokenType.SEMI, "セミコロンがありません")
        return _stmt.ReturnStmtNode(
            return_token.line,
            return_token.column,
            return_token.len,
             self.new_id(), None,
            expr
        )
        
    def fndefine_node(self):
        define_token = self.advance()
        owns = self.Possession()
        types = self.type()
        id_token = self.consume(TokenType.ID, "識別子がありません。")
        self.consume(TokenType.LPAREN, "かっこ '(' がありません")
        args:list[_expr.VariableNode] = []
        arg_types:list[_type.TypeNode] = []
        arg_owns:list[Possession] = []
        if self.peek().type != TokenType.RPAREN:
            while True:
                own_ast = self.Possession()
                type_ast = self.type()
                id_tok = self.consume(TokenType.ID, "識別子が必要です")
                if self.peek().type == TokenType.ANCHOR_BANG:
                    self.advance()
                    args.append(_expr.VariableNode(
                        id_tok.line, id_tok.column, id_tok.len,  self.new_id(), None,
                        None, id_tok.value, _expr.AccessModifier.ANCHOR))
                else:
                    args.append(_expr.VariableNode(
                        id_tok.line,id_tok.column, id_tok.len,  self.new_id(), None,
                        None, id_tok.value, _expr.AccessModifier.NONE))

                arg_owns.append(own_ast)
                arg_types.append(type_ast)

                if self.peek().type == TokenType.COMMA:
                    self.advance()
                    continue
                break
        self.consume(TokenType.RPAREN, "かっこ ')' がありません")
        body = self._Stmt_entry()
        if body is None:
            self.CallError("Body不明", _expr.VariableNode(
                define_token.line, define_token.column, define_token.len,  self.new_id(), None,
                None, define_token.value))
            
        return _stmt.FunctionDefineNode(
                define_token.line,
                define_token.column,
                define_token.len,
                 self.new_id(), None,
                _expr.VariableNode(id_token.line, id_token.column, id_token.len,  self.new_id(), None, None, id_token.value),
                body,
                args,
                arg_types,
                arg_owns,
                types,
                owns
            )
    
    def block_node(self):
        token = self.consume(TokenType.LBRACE, "なんだよ！！！")
        stmts: list[_stmt.Stmt] = []
        while (not self.is_at_end()) and self.peek().type != TokenType.RBRACE:
            stmt = self._Stmt()
            if stmt is None:  # type: ignore
                continue
            if isinstance(stmt, _stmt.ImportNode):
                self.CallError(
                    "トップレベル以外でのImport使用。",
                    stmt,
                    help=[KinakoHelp("トップレベルでのみImportを使用してください。")]
                )
            stmts.append(stmt)
        self.consume(TokenType.RBRACE, "blockが閉じられていません。")
        return _stmt.BlockNode(token.line, token.column, token.len,  self.new_id(), None, stmts)
    
    def let_node_entry(self):   
        checkpoint = self.pos
        error_checkpoint = len(self.error) 

        try:
            # ここでパース
            return self.let_node()
        except KinakoSyntaxError:
            # 失敗したら、静かに指を置いて戻る
            self.pos = checkpoint
            self.error = self.error[:error_checkpoint]
            
            expr = self._expr_entry()
            self.consume(TokenType.SEMI, "セミコロンがありません！")
            return _stmt.ExprStmtNode(expr.line, expr.col, expr.len,  self.new_id(), None, expr)
    
    def let_node(self):
        current = self.peek()
        Possession = self.Possession()
        types = self.type()
        name = self.consume(TokenType.ID, "識別子がありません！！")
        isatmark = self.peek().type == TokenType.ANCHOR_BANG

        variable:_expr.VariableNode
        if isatmark:
            self.advance()
            variable = _expr.VariableNode(
                name.line, name.column, name.len,  self.new_id(), None, None, name.value, _expr.AccessModifier.ANCHOR)
        else:
            variable = _expr.VariableNode(
                name.line, name.column, name.len,  self.new_id(), None, None, name.value, _expr.AccessModifier.NONE)
        
        if self.peek().type == TokenType.SEMI:
            self.consume(TokenType.SEMI, "セミコロンがありません！")
            return _stmt.LetStmt(current.line, current.column, current.len,  self.new_id(), None, Possession, types, variable, None)
        self.consume(TokenType.ASSIGN, "'='がないです。代入が完成しません")
        expr = self._expr_entry()
        self.consume(TokenType.SEMI, "セミコロンがありません！")
        return _stmt.LetStmt(current.line, current.column, current.len,  self.new_id(), None, Possession, types, variable, expr)
    
    def Possession(self) -> Possession:
        """
        Possessionをゲットしちゃう
        """
        flag = self.TOKEN_TO_EFFECTS[self.advance().type]
        if self.peek().type == TokenType.LBRACKET:
            self.consume(TokenType.LBRACKET, "[がありません！")
            generic = self.Possession()
            self.consume(TokenType.RBRACKET, "]がありません！")
            return Possession(flag, generic)
        return Possession(flag, None)

    def type(self) -> _type.TypeNode:
        typetoken = self.peek()
        match (typetoken.type):
            case TokenType.tLIST:
                self.advance()
                self.consume(TokenType.LBRACKET, "[がありません！")
                element = self.type()
                self.consume(TokenType.RBRACKET, "]がありません！")
                return _type.ListTypeNode(typetoken.line, typetoken.column, typetoken.len,  self.new_id(), None, element)
            case TokenType.ID:
                self.advance()
                return _type.UserDefinedTypeNode(typetoken.line, typetoken.column, typetoken.len,  self.new_id(), None, typetoken.value)
            case t if t in NOT_GEMERIC:
                self.advance()
                return _type.PrimitiveTypeNode(typetoken.line, typetoken.column, typetoken.len,  self.new_id(), None, typetoken.type)
            case _:
                self.CallError(f"不明な型トークン'{typetoken.value}'。", ASTNode(typetoken.line, typetoken.column, typetoken.len, self.new_id(), None))







# point nemo!! <- Good!!







    def left_binary_op(
            self, next_func: Callable[[], _expr.Expr], token_types: list[TokenType],
            node_factory: Callable[[Token, _expr.Expr, _expr.Expr], _expr.Expr]
            ) -> _expr.Expr:
        node = next_func() 

        while self.peek().type in token_types:
            operator_token = self.advance()

            right = next_func()

            # 左結合
            node = node_factory(operator_token, node, right)
        
        return node
    
    def right_binary_op(
            self, next_func: Callable[[], _expr.Expr], token_types: list[TokenType],
            node_factory: Callable[[Token, _expr.Expr, _expr.Expr], _expr.Expr]
            ) -> _expr.Expr:
        node = next_func()
        
        if self.peek().type in token_types:
            operator_token = self.advance()
            right = self.right_binary_op(next_func, token_types, node_factory)
            node = node_factory(operator_token, node, right)
        return node
    

    def _make_binary(self, tok: Token, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """算術演算・比較演算用の工場"""
        return _expr.BinaryOperationNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right,
            id= self.new_id(),
            scopeid=None,
        )

    def _make_logical(self, tok: Token, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """&& や || などの論理演算用の工場"""
        return _expr.LogicalOperationNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right,
            id= self.new_id(),
            scopeid=None,
        )

    def _make_assign(self, tok: Token, left: _expr.Expr, right: _expr.Expr) -> _expr.Expr:
        """代入用の工場"""
        return _expr.AssignNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right,
            id= self.new_id(),
            scopeid=None,
        )


    def _expr_entry(self) -> _expr.Expr:
        return self.assignment()
    
    def assignment(self) -> _expr.Expr:
        return self.right_binary_op(self.logical_or, [TokenType.ASSIGN], self._make_assign)

    def logical_or(self) -> _expr.Expr:
        return self.left_binary_op(self.logical_and, [TokenType.LOGIC_OR], self._make_logical)

    def logical_and(self) -> _expr.Expr:
        return self.left_binary_op(self.equality, [TokenType.LOGIC_AND], self._make_logical)

    def equality(self) -> _expr.Expr:
        return self.left_binary_op(self.comparison, [TokenType.EQ, TokenType.NE], self._make_binary)

    def comparison(self) -> _expr.Expr:
        return self.left_binary_op(self.term, [
            TokenType.LABRACKET, TokenType.GE, TokenType.RABRACKET, TokenType.LE
        ], self._make_binary)

    def term(self) -> _expr.Expr:
        return self.left_binary_op(self.factor, [TokenType.PLUS, TokenType.MINUS], self._make_binary)

    def factor(self) -> _expr.Expr:
        return self.left_binary_op(self.prefix, [TokenType.MULT, TokenType.DIV], self._make_binary)
    
    def prefix(self) -> _expr.Expr:
        # prefix (前置演算)
        if self.match(TokenType.MINUS, TokenType.PLUS):
            operator_token = self.previous()
            right = self.prefix() # 自分自身を再帰的に呼ぶ
            return _expr.UnaryOperationNode(
                operator_token.line, operator_token.column, operator_token.len,  self.new_id(), None,
                None, operator_token.type, right
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
                node = _expr.IndexAccessNode(node.line, node.col, node.len,  self.new_id(), None, None, index, node)
            elif self.match(TokenType.DOT): # プロパティアクセス a.b
                name = self.consume(TokenType.ID, "プロパティ名が必要です。")
                node = _expr.MemberAccessNode(node.line, node.col, node.len,  self.new_id(), None, None, node,
                                              _expr.VariableNode(name.line, name.column, name.len, self.new_id(), None, None, name.value))
            else:
                break
        
        return node
    
    def primary(self) -> _expr.Expr:
        current = self.peek()
        note:list[KinakoHelp] = []
        match(current.type):
            case TokenType.NUMBER:
                self.advance()
                return _literal.IntLiteralNode(current.line, current.column, current.len,  self.new_id(), None, None, int(current.value))
            case TokenType.DECIMAL:
                self.advance()
                return _literal.FloatLiteralNode(current.line, current.column, current.len,  self.new_id(), None, None, float(current.value))
            case TokenType.ID:
                self.advance()
                isatmark = self.peek().type == TokenType.ANCHOR_BANG
                if isatmark:
                    self.advance()
                    return _expr.VariableNode(
                        current.line, current.column, current.len,  self.new_id(), None, None, current.value,
                        _expr.AccessModifier.ANCHOR
                        )
                return _expr.VariableNode(
                        current.line, current.column, current.len,  self.new_id(), None, None, current.value,
                        _expr.AccessModifier.NONE
                        )
            case TokenType.LPAREN:
                self.advance()
                expr = self._expr_entry()
                self.consume(TokenType.RPAREN, "')'が閉じられていません！！")
                return expr
            case TokenType.STRING:
                self.advance()
                return _literal.StrLiteralNode(current.line, current.column, current.len,  self.new_id(), None, None, current.value)
            case TokenType.LET | TokenType.MUT | TokenType.CONST:
                note.append(
                    KinakoHelp(
                        "もしかしたら、宣言文が不完全ではありませんか？"
                    )
                )
                self.CallError(f"不明なトークン{current.value}。",
                               ASTNode(current.line, current.column, current.len, self.new_id(), None), [], note)
            case _:
                self.CallError(f"不明なトークン{current.value}。",
                               ASTNode(current.line, current.column, current.len, self.new_id(), None), [], note)
    
    def _finish_call(self, expr:_expr.Expr) -> _expr.Expr:
        # 関数呼び出し
        func = self.advance()
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
        return _expr.CallNode(func.line, func.column, end.column - func.column,  self.new_id(), None, None, expr, args)