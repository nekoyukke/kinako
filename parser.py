from __future__ import annotations
from tokens import Token, TokenType 
from myast import *
import utils
from typing import Callable

def ast(Tokens:list[Token], source: str):
    pos = 0

    def ad():
        nonlocal pos
        pos+=1
        if (pos >= len(Tokens)):
            return
        return
    def cu(name:str = "unkwon"):
        nonlocal pos
        if (pos >= len(Tokens)):
            raise utils.ParseError("out of range", Tokens[pos-1].line, Tokens[pos-1].column, source, name, Tokens[pos-1].String)
        return Tokens[pos]
    
    def ex(tok:TokenType, name:str = "unkwon", message:str = "unkown"):
        nonlocal pos
        cua = cu(name)
        ad()
        if (cua.type == tok):
            return cua
        else:
            raise utils.ParseError(message,cua.line,cua.column,source,name, cua.String)
    
    def binary_op(next_func:Callable[[], Expr], token_types: list[TokenType]) -> Expr:
        nod = next_func()  # 1つ上の優先順位を呼ぶ
        cus = cu("binary_op")
        while cus.type in token_types:
            ad()
            # 左結合の木を作る
            nod = BinaryOpNode(nod, cus, next_func())
            cus = cu("binary_op")
        return nod
    
    def program(type:TokenType):
        exp = Program([])
        while cu("program").type != type:
            exp.blocks += [stmt()]
        return exp
    
    def stmt() -> Stmt:
        match(cu().type):
            case TokenType.VAL | TokenType.CONST | TokenType.LET:
                return Declaration()
            case TokenType.LBRACE:
                return Block()
            case TokenType.IF:
                return If()
            case TokenType.FOR:
                return For()
            case TokenType.WHILE:
                return While()
            case TokenType.RETURN:
                return Return()
            case TokenType.FN:
                return Define()
            case TokenType.IMPORT:
                return Import()
            case _:
                exp = expr()
                ex(TokenType.SEMI, "Stmt in Expr", "';' is required")
                return ExprStmtNode(exp)
    
    def Import() -> Stmt:
        tok = cu()
        ad()
        expr_import = expr()
        semi = ex(TokenType.SEMI)
        return ImportNode(tok.line, tok.column, semi.column - tok.column + 1, expr_import, tok)

    def Block() -> Stmt:
        ex(TokenType.LBRACE, "block", "Expected '{'")
        
        lifetime: Optional[LifetimeNode] = None
        captures: list[VariableNode] = []

        # ライフタイムの解析: `a
        if cu().type == TokenType.BACKQUOTE:
            ad() # ` を消費
            # ` の直後は識別子（名前）を期待
            lt_tok = ex(TokenType.ID, "lifetime", "Expected name after '`'")
            lifetime = LifetimeNode("`" + lt_tok.String, lt_tok)

        # キャプチャリストの解析: [id1, id2, ...]
        if cu().type == TokenType.LBRACKET:
            ad() # [ を消費
            if cu().type != TokenType.RBRACKET: # 空でない場合
                while True:
                    id_tok = ex(TokenType.ID, "capture", "Expected identifier in capture list")
                    captures.append(VariableNode(id_tok.String, id_tok))
                    
                    if cu().type == TokenType.COMMA:
                        ad()
                        continue
                    break
            ex(TokenType.RBRACKET, "block", "Expected ']'")

        # 内部の Stmt を解析
        stmts: list[Stmt] = []
        while cu().type != TokenType.RBRACE:
            stmts.append(stmt())
            
        ex(TokenType.RBRACE, "block", "Expected '}'")
        
        return BlockNode(stmts, lifetime, captures)
            
    
    def If() -> Stmt:
        # 'if' を消費
        ex(TokenType.IF, "if")
        
        # 条件と実行文
        condition = expr()
        then_stmt = stmt()
        
        else_stmt: Optional[Stmt] = None

        if cu().type == TokenType.ELIF:
            # elif を「if」として再帰的にパースする
            else_stmt = Elif_helper()
        elif cu().type == TokenType.ELSE:
            ad()
            else_stmt = stmt()
            
        return IfStmtNode(condition, then_stmt, else_stmt)

    def Elif_helper() -> Stmt:
        # elif トークンを消費して、中身は if と同じように処理
        ex(TokenType.ELIF, "elif")
        condition = expr()
        then_stmt = stmt()
        
        else_stmt = None
        if cu().type == TokenType.ELIF:
            else_stmt = Elif_helper() # さらに続くなら再帰
        elif cu().type == TokenType.ELSE:
            ad()
            else_stmt = stmt()
            
        return IfStmtNode(condition, then_stmt, else_stmt)

    
    def For() -> Stmt:
        # For <Id> in <Expr> <Stmt>
        fortok = ex(TokenType.FOR, "for")
        
        # ループ変数の取得 i
        var_tok = ex(TokenType.ID, "for", "Expected identifier after 'for'")
        iterator = VariableNode(var_tok.String, var_tok)
        
        # INキーワードのチェック
        ex(TokenType.IN, "for", "Expected 'in' after for-variable")
        
        # 繰り返す対象の式
        iterable = expr()
        end = cu()
        
        body = stmt()
        return ForNode(fortok.line, fortok.column, end.column - fortok.column + 1, iterator, iterable, body)
    
    def While() -> Stmt:
        # While <Expr> <Stmt> else <Stmt>
        ex(TokenType.WHILE)
        condition = expr()
        body = stmt()
        return WhileStmtNode(condition, body)
    
    def Return() -> Stmt:
        # Return <Expr>
        ret = cu()
        ad()
        if cu().type == TokenType.SEMI:
            retstmt = ReturnStmtNode(ret)
        else:
            retstmt = ReturnStmtNode(ret, expr())
        ex(TokenType.SEMI)
        return retstmt
        
    
    def Define() -> Stmt:
        # define <type> <Id> (<Param>...) <Stmt>
        fn = cu()
        ad()
        types = typenode()
        idtok = ex(TokenType.ID)
        ex(TokenType.LPAREN)
        args:list[Params] = []
        if cu().type != TokenType.RPAREN:
            while True:
                type_tok = typenode()
                id_tok = ex(TokenType.ID, "capture", "Expected identifier in capture list")
                args.append(Params(type_tok, VariableNode(id_tok.String, id_tok)))

                if cu().type == TokenType.COMMA:
                    ad()
                    continue
                break
        rpaern = ex(TokenType.RPAREN)
        body = stmt()
        return FunctionDefNode(
                fn.line,
                fn.column,
                rpaern.column - fn.column + 1,
                idtok,
                body,
                FunctionTypeNode(
                    TokenType.tFUNCTION.name,
                    Token.zero(),
                    False,
                    [i.types for i in args],
                    types
                    ),
                args
            )
    
    def Declaration() -> Stmt:
        # Todo
        # let <Type> <Ident>;
        # let <Type> <Ident> = <Expr>;
        # Const <Type> <Ident> = <Expr>;
        # Val <Type> <Ident>;
        # Val <Type> <Ident> = <Expr>;
        
        # load cu
        Typetok = cu("Declaration")
        ad()
        type = typenode()
        lefttok = ex(TokenType.ID)
        left = VariableNode(lefttok.String, lefttok)
        right:Optional[Expr] = None
        if cu("Declaration").type == TokenType.ASSIGN:
            ex(TokenType.ASSIGN, "Declaration", "Dec")
            right = expr()
        semi = ex(TokenType.SEMI, "Declaration", "';' is required")
        match (Typetok.type):
            case TokenType.VAL:
                return DeclarationNode(Typetok.line, Typetok.column, semi.column - semi.column + 1, left, right, type, VariableType.VAL)
            case TokenType.CONST:
                return DeclarationNode(Typetok.line, Typetok.column, semi.column - semi.column + 1, left, right, type, VariableType.CONST)
            case TokenType.LET:
                return DeclarationNode(Typetok.line, Typetok.column, semi.column - semi.column + 1, left, right, type, VariableType.LET)
            case _:
                raise

    def typenode() -> TypeNode:
        typetok = cu()
        
        if (typetok.type == TokenType.tLIST):
            ad()
            # もしリストなら
            ex(TokenType.LABRACKET, "type", "it dont have '<' Token in type call")
            nod = typenode()
            nod = ListTypeNode(typetok.String, typetok, False, nod)
            ex(TokenType.RABRACKET, "type", "it dont have '>' Token in type call")
            return nod
        if (typetok.type == TokenType.tPTR):
            ad()
            ex(TokenType.LABRACKET, "type", "it dont have '<' Token in type call")
            nod = typenode()
            nod = PointerTypeNode(typetok.String, typetok, False, nod)
            ex(TokenType.RABRACKET, "type", "it dont have '>' Token in type call")
            return nod
        if (typetok.type == TokenType.tMUT):
            ad()
            ex(TokenType.LABRACKET, "type", "it dont have '<' Token in type call")
            nod = typenode()
            nod = MutTypeNode(typetok.String, typetok, False, nod)
            ex(TokenType.RABRACKET, "type", "it dont have '>' Token in type call")
            return nod
        if (typetok.type == TokenType.tBORROW):
            ad()
            ex(TokenType.LABRACKET, "type", "it dont have '<' Token in type call")
            nod = typenode()
            nod = BorrowTypeNode(typetok.String, typetok, False, nod)
            ex(TokenType.RABRACKET, "type", "it dont have '>' Token in type call")
            return nod
        ad()
        return TypeNode(typetok.String, typetok, False)
    
    def expr() -> Expr:
        """
        'To Do'? no no
        'Do To'.
        順位,関数名（レベル）,演算子,特徴・備考
        1,Primary / Postfix,"f(), x.y, x++, x--",++/-- は後置なら最強
        2,Unary / Prefix,"!, ~, -x, ++x, !!, ?!, %%!",Reject系はここ。右から左へ結合
        3,Exponentiation,**,べき乗（右結合）
        4,Multiplicative,"*, /, //, %",算術計算（乗除）
        5,Additive,"+, -, &",&が文字列結合ならここでOK
        6,Bitwise Shift,"<<, >>",ビットシフト
        7,Relational,"<, <=, >, >=",大小比較
        8,Equality,"==, !=, ===, !==, <=>",宇宙船演算子はここ
        9,Bitwise AND,& (単一),ビットAND
        10,Bitwise XOR,^,ビットXOR
        11,Bitwise OR,|,ビットOR
        12,Logical XOR,^^,排他的論理和
        13,Logical AND,&&,
        14,Logical OR,||,
        15,Coalescing,"??, %%%, ?:",Elvis系。論理演算より弱く設定
        16,Range,..,範囲作成
        17,Assignment,"=, +=, ?= ...",最も弱い（右結合）
        """
        return Assignment()

    def Assignment() -> Expr:
        nod = Range()
        cus = cu("assignment")
        if (cus.type in(
                                TokenType.ASSIGN,
                                TokenType.ADD_ASSIGN,
                                TokenType.SUB_ASSIGN,
                                TokenType.MUL_ASSIGN,
                                TokenType.DIV_ASSIGN,
                                TokenType.MOD_ASSIGN,
                                TokenType.NULLCOALESCING_ASSIGN,
                                TokenType.NONECOALESCING_ASSIGN
                            )
                        ):
            ad()
            right = Assignment() 
            return AssginNode(nod, right, cus, AssginType[cus.type.name])
        return nod
    
    def Range() -> Expr:
        nod = Coalescing()
        if cu().type == TokenType.DOUBLEDOT:
            tok = ex(TokenType.DOUBLEDOT)
            right = Coalescing()
            if cu().type == TokenType.DOUBLEDOT:
                raise utils.ParseError("Range cannot be chained", cu().line, cu().column, source, "Range", cu().String)
            return BinaryOpNode(nod, tok, right)
        return nod
    
    def Coalescing() -> Expr:
        return binary_op(LogicalOR, [TokenType.NULLCOALESCING,
        TokenType.NONECOALESCING,
        TokenType.ELVIS,
        TokenType.NULLREJECT,
        TokenType.NONEREJECT,
        TokenType.REJECT])
    
    def LogicalOR() -> Expr:
        return binary_op(LogicalAND, [TokenType.LOGICAND])
    
    def LogicalAND() -> Expr:
        return binary_op(LogicalXOR, [TokenType.LOGICXOR])
    
    def LogicalXOR() -> Expr:
        return binary_op(BitwiseOR, [TokenType.LOGICOR])
    
    def BitwiseOR() -> Expr:
        return binary_op(BitwiseAND, [TokenType.BITOR])
    
    def BitwiseAND() -> Expr:
        return binary_op(BitwiseXOR, [TokenType.BITAND])
    
    def BitwiseXOR() -> Expr:
        return binary_op(Equality, [TokenType.BITXOR])
    
    def Equality() -> Expr:
        return binary_op(Relational, [TokenType.EQ,
        TokenType.NE,
        TokenType.EQSTRICT,
        TokenType.NESTRICT])
    
    def Relational() -> Expr:
        return binary_op(BitwiseShift, [TokenType.LABRACKET,
        TokenType.RABRACKET,
        TokenType.LE,
        TokenType.GE,
        TokenType.CMP])
    
    def BitwiseShift() -> Expr:
        return binary_op(Additive, [
            TokenType.LSHIFT,
            TokenType.RSHIFT
        ])
    
    def Additive() -> Expr:
        return binary_op(Multiplicative, [TokenType.PLUS, TokenType.MINUS])
    
    def Multiplicative() -> Expr:
        return binary_op(Exponentiation, [TokenType.MULT, TokenType.DIV])
    
    def Exponentiation() -> Expr:
        # まず左辺（Prefix）を読み込む
        nod = Prefix()
        
        # 次が ** だったら
        if cu().type == TokenType.EXP: # EXP = **
            tok = cu()
            ad()
            # 右辺として「自分自身」を呼ぶことで、右側の ** を先に処理させる
            right = Exponentiation()
            return BinaryOpNode(nod, tok, right)
            
        return nod
    
    def Prefix() -> Expr:
        cus = cu()
        if cus.type in (TokenType.MULT, TokenType.ADD):
            ad()
            return UnaryOpNode(cus, Prefix()) # 再帰して重ね掛け対応
        return unary() # postfixへ

    def unary() -> Expr:
        cus = cu()
        if cus.type in (TokenType.LOGICNOT, TokenType.MINUS, TokenType.BITNOT):
            ad()
            return UnaryOpNode(cus, unary()) # 再帰して重ね掛け対応
        return postfix() # postfixへ

    def postfix() -> Expr:
        node: Expr = prime() # まず核(123や変数名)を拾う

        while True:
            cus = cu("postfix")
            if cus.type == TokenType.DOT:
                ad()
                member = ex(TokenType.ID)
                node = MemberAccessNode(node, VariableNode(member.String, member))
            elif cus.type == TokenType.LBRACKET:
                ad()
                index = expr()
                ex(TokenType.RBRACKET)
                node = IndexAccessNode(node, index)
            elif cus.type == TokenType.LPAREN:
                # primeの中にあった関数呼び出しロジックをここに移動！
                node = call_logic(node) 
            else:
                break
        return node
    
    def call_logic(node:Expr):
        # 関数呼び出し
        ad()
        # a(1,2)
        #   ^
        args: list[Expr] = []
        while (cu("defcall prime 2").type != TokenType.RPAREN):
            op = expr()
            args.append(op)
            if (cu("defcall prime 3").type == TokenType.COMMA):
                ex(TokenType.COMMA, "prime", "COMMA is hasnt")
                continue
            else:
                break
        utils.logging.debug(cu())
        ex(TokenType.RPAREN,"prime","dont have )")
        return CallExprNode(node, args)

    def prime() -> Expr:
        cus = cu("prime one")
        if (cus.type == TokenType.NUMBER):
            ad()
            if isinstance(cus.value, str|float):
                raise
            return NumberNode(cus.value, cus, 10)
        elif (cus.type == TokenType.ID):
            ad()
            if isinstance(cus.value, int|float):
                raise
            return VariableNode(cus.value, cus)
        elif (cus.type == TokenType.LPAREN):
            ad()
            nod = expr()
            ex(TokenType.RPAREN, "prime", "it dont have ')' Token")
            return nod
        elif (cus.type == TokenType.TRUE):
            ad()
            return BoolNode(cus, True)
        elif (cus.type == TokenType.FALSE):
            ad()
            return BoolNode(cus, False)
        elif (cus.type == TokenType.NONE):
            ad()
            return NoneNode(cus)
        elif (cus.type == TokenType.NULL):
            ad()
            return NullNode(cus)
        elif (cus.type == TokenType.STR):
            ad()
            return StringNode(cus.String, cus)
        raise utils.ParseError("unkonw Tokens",cus.line,cus.column,source,"prime", cus.String)
    nod = program(TokenType.END)
    return nod