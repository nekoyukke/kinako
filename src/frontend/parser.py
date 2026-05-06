from typing import Generic
from typing import Callable

from src.frontend.models.token import Token
from src.frontend.models.tokentype import TokenType, NOT_GEMERIC
import src.frontend.models.stmt as _stmt
import src.frontend.models.expr as _expr
import src.frontend.models.literal as _literal
import src.frontend.models.type as _type
from src.frontend.models.base import S,P, ASTNode


from src.utils.error.base import KinakoRelatedInfo, KinakoHelp
from src.utils.error.syntax import KinakoSyntaxError


from src.core.ownership import Ownership

class Parser(Generic[S,P]):
    TOKEN_TO_EFFECTS: dict[TokenType, Ownership] = {
        TokenType.LET: Ownership.OWNED | Ownership.READ,
        TokenType.MUT: Ownership.OWNED | Ownership.WRITE,
        TokenType.CONST: Ownership.OWNED | Ownership.READ | Ownership.FREEZE,
        TokenType.SHARED: Ownership.OWNED | Ownership.READ | Ownership.SHARED,
    }

    def __init__(self, tokens: list[Token] ,source:str) -> None:
        self.tokens: list[Token] = tokens
        self.source: str = source
        self.pos = 0
        self.error: list[KinakoSyntaxError] = []
    
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
        self.CallError(message, ASTNode(current.line, current.column, current.len))
    
    def CallError(
            self, message:str ,node:ASTNode[S,P],
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
    
    def _Program(self) -> _stmt.Program[S,P]:
        stmts: list[_stmt.Stmt[S,P]] = []
        import_stmts: list[_stmt.ImportNode[S,P]] = []
        while not self.is_at_end():
            stmt = self._Stmt_entry()
            if stmt is None:
                continue
            if isinstance(stmt, _stmt.ImportNode):
                import_stmts.append(stmt)
                continue
            stmts.append(stmt)
            continue
        return _stmt.Program(0,0,0,stmts, [], import_stmts)
    
    def _Stmt_entry(self) -> None | _stmt.Stmt[S,P] | _stmt.ImportNode[S,P]:
        try:
            return self._Stmt()
        except KinakoSyntaxError:
            self.synchronize()
        return
    

    def _Stmt(self):
        match(self.peek().type):
            case TokenType.LET | TokenType.CONST | TokenType.MUT | TokenType.SHARED:
               return self.let_node_entry()
            case TokenType.ANCHOR:
                return self.anchor()
            case TokenType.FN:
                return self.fndefinenode()
            case TokenType.FOR:
                return self.fornode()
            case TokenType.WHILE:
                return self.whilenode()
            case TokenType.RETURN:
                return self.returnnode()
            case TokenType.IMPORT:
                return self.importnode()
            case TokenType.LBRACE:
                return self.blocknode()
            case _:
                expr = self._expr_entry()
                self.consume(TokenType.SEMI, "セミコロンがありません！")
                return _stmt.ExprStmtNode(expr.line, expr.col, expr.len, expr)
        
    def fndefinenode(self):
        return
    
    def blocknode(self):
        token = self.consume(TokenType.LBRACE, "なんだよ！！！")
        stmts: list[_stmt.Stmt[S,P]] = []
        while (not self.is_at_end()) or self.peek().type != TokenType.RBRACE:
            stmt = self._Stmt_entry()
            if stmt is None:
                continue
            if isinstance(stmt, _stmt.ImportNode):
                self.CallError(
                    "トップレベル以外でのImport使用。",
                    stmt,
                    help=[KinakoHelp("トップレベルでのみImportを使用してください。")]
                )
            stmts.append(stmt)
        self.consume(TokenType.RBRACE, "blockが閉じられていません。")
        return _stmt.BlockNode(token.line, token.column, token.len, stmts)
    
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
            return _stmt.ExprStmtNode(expr.line, expr.col, expr.len, expr)
    
    def let_node(self):
        current = self.peek()
        ownership = self.ownership()
        types = self.type()
        name = self.consume(TokenType.ID, "識別子がありません！！")
        isatmark = self.peek().type == TokenType.ANCHOR_BANG

        variable:_expr.VariableNode[S,P]
        if isatmark:
            self.advance()
            variable = _expr.VariableNode(name.line, name.column, name.len, None, name.value, _expr.AccessModifier.ANCHOR, None)
        else:
            variable = _expr.VariableNode(name.line, name.column, name.len, None, name.value, _expr.AccessModifier.NONE, None)
        
        if self.peek().type == TokenType.SEMI:
            self.consume(TokenType.SEMI, "セミコロンがありません！")
            return _stmt.LetStmt(current.line, current.column, current.len, ownership, types, variable, None)
        self.consume(TokenType.ASSIGN, "'='がないです。代入が完成しません")
        expr = self._expr_entry()
        self.consume(TokenType.SEMI, "セミコロンがありません！")
        return _stmt.LetStmt(current.line, current.column, current.len, ownership, types, variable, expr)

    def ownership(self) -> Ownership:
        now: Ownership = Ownership.NONE
        current = self.advance()
        now |= self.TOKEN_TO_EFFECTS[current.type]
        while self.peek().type in self.TOKEN_TO_EFFECTS:
            current = self.advance()
            now |= self.TOKEN_TO_EFFECTS[current.type]
        return now

    def type(self) -> _type.TypeNode[S,P]:
        typetoken = self.peek()
        match (typetoken.type):
            case TokenType.tLIST:
                self.advance()
                self.consume(TokenType.LBRACKET, "[がありません！")
                element = self.type()
                self.consume(TokenType.RBRACKET, "]がありません！")
                return _type.ListTypeNode(typetoken.line, typetoken.column, typetoken.len, element)
            case TokenType.ID:
                self.advance()
                return _type.UserDefinedTypeNode(typetoken.line, typetoken.column, typetoken.len, typetoken.value)
            case t if t in NOT_GEMERIC:
                self.advance()
                return _type.PrimitiveTypeNode(typetoken.line, typetoken.column, typetoken.len, typetoken.type)
            case _:
                self.CallError(f"不明な型トークン'{typetoken.value}'。", ASTNode(typetoken.line, typetoken.column, typetoken.len))







# point nemo!! <- Good!!







    def left_binary_op(
            self, next_func: Callable[[], _expr.Expr[S, P]], token_types: list[TokenType],
            node_factory: Callable[[Token, _expr.Expr[S, P], _expr.Expr[S, P]], _expr.Expr[S, P]]
            ) -> _expr.Expr[S, P]:
        node = next_func() 

        while self.peek().type in token_types:
            operator_token = self.advance()

            right = next_func()

            # 左結合
            node = node_factory(operator_token, node, right)
        
        return node
    
    def right_binary_op(
            self, next_func: Callable[[], _expr.Expr[S, P]], token_types: list[TokenType],
            node_factory: Callable[[Token, _expr.Expr[S, P], _expr.Expr[S, P]], _expr.Expr[S, P]]
            ) -> _expr.Expr[S, P]:
        node = next_func()
        
        if self.peek().type in token_types:
            operator_token = self.advance()
            right = self.right_binary_op(next_func, token_types, node_factory)
            node = node_factory(operator_token, node, right)
        return node
    

    def _make_binary(self, tok: Token, left: _expr.Expr[S, P], right: _expr.Expr[S, P]) -> _expr.Expr[S, P]:
        """算術演算・比較演算用の工場"""
        return _expr.BinaryOperationNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right
        )

    def _make_logical(self, tok: Token, left: _expr.Expr[S, P], right: _expr.Expr[S, P]) -> _expr.Expr[S, P]:
        """&& や || などの論理演算用の工場"""
        return _expr.LogicalOperationNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right
        )

    def _make_assign(self, tok: Token, left: _expr.Expr[S, P], right: _expr.Expr[S, P]) -> _expr.Expr[S, P]:
        """代入用の工場"""
        return _expr.AssignNode(
            line=tok.line,
            col=tok.column,
            len=tok.len,
            place=None,
            op=tok.type,
            left=left,
            right=right
        )


    def _expr_entry(self) -> _expr.Expr[S,P]:
        return self.assignment()
    
    def expression(self) -> _expr.Expr[S, P]:
        return self.assignment()

    def assignment(self) -> _expr.Expr[S, P]:
        return self.right_binary_op(self.logical_or, [TokenType.ASSIGN], self._make_assign)

    def logical_or(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.logical_and, [TokenType.LOGIC_OR], self._make_logical)

    def logical_and(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.equality, [TokenType.LOGIC_AND], self._make_logical)

    def equality(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.comparison, [TokenType.EQ, TokenType.NE], self._make_binary)

    def comparison(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.term, [
            TokenType.LABRACKET, TokenType.GE, TokenType.RABRACKET, TokenType.LE
        ], self._make_binary)

    def term(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.factor, [TokenType.PLUS, TokenType.MINUS], self._make_binary)

    def factor(self) -> _expr.Expr[S, P]:
        return self.left_binary_op(self.prefix, [TokenType.MULT, TokenType.DIV], self._make_binary)
    
    def prefix(self) -> _expr.Expr[S, P]:
        # prefix (前置演算)
        if self.match(TokenType.MINUS, TokenType.PLUS):
            operator_token = self.previous()
            right = self.prefix() # 自分自身を再帰的に呼ぶ
            return _expr.UnaryOperationNode(
                operator_token.line, operator_token.column, operator_token.len,
                None, operator_token.type, right
            )
        
        return self.postfix()

    def postfix(self) -> _expr.Expr[S, P]:
        # postfix (後置演算: 関数呼び出し、配列アクセス、プロパティ)
        node:_expr.Expr[S,P] = self.primary()

        while True:
            if self.match(TokenType.LPAREN): # 関数呼び出し a()
                node = self._finish_call(node)
            elif self.match(TokenType.LBRACKET): # インデックス a[0]
                index = self.expression()
                self.consume(TokenType.RBRACKET, "']'がありません。トークン不足！")
                node = _expr.IndexAccessNode(node.line, node.col, node.len, None, index, node)
            elif self.match(TokenType.DOT): # プロパティアクセス a.b
                name = self.consume(TokenType.ID, "プロパティ名が必要です。")
                node = _expr.MemberAccessNode(node.line, node.col, node.len, None, node, name.value)
            else:
                break
        
        return node
    
    def primary(self) -> _expr.Expr[S,P]:
        current = self.peek()
        match(current.type):
            case TokenType.NUMBER:
                self.advance()
                return _literal.IntLiteralNode(current.line, current.column, current.len, None, int(current.value))
            case TokenType.DECIMAL:
                self.advance()
                return _literal.FloatLiteralNode(current.line, current.column, current.len, None, float(current.value))
            case TokenType.ID:
                self.advance()
                isatmark = self.peek().type == TokenType.ANCHOR_BANG
                if isatmark:
                    self.advance()
                    return _expr.VariableNode(
                        current.line, current.column, current.len, None, current.value,
                        _expr.AccessModifier.ANCHOR, None
                        )
                return _expr.VariableNode(
                        current.line, current.column, current.len, None, current.value,
                        _expr.AccessModifier.NONE, None
                        )
            case TokenType.LPAREN:
                self.advance()
                expr = self._expr_entry()
                self.consume(TokenType.RPAREN, "')'が閉じられていません！！")
                return expr
            case TokenType.STRING:
                self.advance()
                return _literal.StrLiteralNode(current.line, current.column, current.len, None, current.value)
            case _:
                self.CallError(f"不明なトークン{current.value}。", ASTNode(current.line, current.column, current.len))
    
    def _finish_call(self, expr:_expr.Expr[S,P]) -> _expr.Expr[S,P]:
        # 関数呼び出し
        func = self.peek()
        self.advance()
        # a(1,2)
        #   ^
        args: list[_expr.Expr[S,P]] = []
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
        return _expr.CallNode(func.line, func.column, end.column - func.column, None, expr, args)

if __name__ == "__main__":
    from src.frontend.lexer import Lexer
    source = """
let shared int a = 10;
"""
    lex = Lexer(source)
    from typing import Any
    toks = lex.tokenize()
    print(toks)
    pas:Parser[Any,Any] = Parser(toks, source)
    res = pas.parse()
    print(res)
    print(pas.error)