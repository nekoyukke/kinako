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
            nod = BinaryOpNode(cus.line, cus.column, cu("binary_op").column - cus.column, nod, cus, next_func())
            cus = cu("binary_op")
        return nod
    
    def program(type:TokenType):
        exp = Program(0,0,0,[])
        while cu("program").type != type:
            exp.blocks += [stmt()]
        return exp
    
    def stmt() -> Stmt:
        match(cu().type):
            case TokenType.VAL | TokenType.CONST | TokenType.LET | TokenType.MUT | TokenType.BORROW:
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
                start = cu()
                exp = expr()
                ex(TokenType.SEMI, "Stmt in Expr", "';' is required")
                end = cu()
                return ExprStmtNode(start.line, start.column, end.column - start.column, exp)
    
    def Import() -> Stmt:
        tok = cu()
        ad()
        expr_import = expr()
        semi = ex(TokenType.SEMI)
        return ImportNode(tok.line, tok.column, semi.column - tok.column + 1, expr_import, tok)

    def Block() -> Stmt:
        lbrace =  ex(TokenType.LBRACE, "block", "Expected '{'")
        
        # 内部の Stmt を解析
        stmts: list[Stmt] = []
        while cu().type != TokenType.RBRACE:
            stmts.append(stmt())
            
        ex(TokenType.RBRACE, "block", "Expected '}'")
        
        return BlockNode(lbrace.line,lbrace.column,1,stmts)
            
    
    def If() -> Stmt:
        # 'if' を消費
        iftok = ex(TokenType.IF, "if")
        
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
            
        return IfStmtNode(iftok.line, iftok.column, 2,condition, then_stmt, else_stmt)

    def Elif_helper() -> Stmt:
        # elif トークンを消費して、中身は if と同じように処理
        iftok = ex(TokenType.ELIF, "elif")
        condition = expr()
        then_stmt = stmt()
        
        else_stmt = None
        if cu().type == TokenType.ELIF:
            else_stmt = Elif_helper() # さらに続くなら再帰
        elif cu().type == TokenType.ELSE:
            ad()
            else_stmt = stmt()
            
        return IfStmtNode(iftok.line, iftok.column, 2,condition, then_stmt, else_stmt)

    
    def For() -> Stmt:
        # For <Id> in <Expr> <Stmt>
        fortok = ex(TokenType.FOR, "for")
        
        # ループ変数の取得 i
        var_tok = ex(TokenType.ID, "for", "Expected identifier after 'for'")
        iterator = VariableNode(var_tok.line, var_tok.column, len(var_tok.String), var_tok.String, var_tok)
        
        # INキーワードのチェック
        ex(TokenType.IN, "for", "Expected 'in' after for-variable")
        
        # 繰り返す対象の式
        iterable = expr()
        end = cu()
        
        body = stmt()
        return ForNode(fortok.line, fortok.column, end.column - fortok.column + 1, iterator, iterable, body)
    
    def While() -> Stmt:
        # While <Expr> <Stmt> else <Stmt>
        whiletok = ex(TokenType.WHILE)
        condition = expr()
        body = stmt()
        return WhileStmtNode(whiletok.line, whiletok.column, len(whiletok.String),condition, body)
    
    def Return() -> Stmt:
        # Return <Expr>
        ret = cu()
        ad()
        if cu().type == TokenType.SEMI:
            retstmt = ReturnStmtNode(ret.line, ret.column, 0, ret)
        else:
            retstmt = ReturnStmtNode(ret.line, ret.column, 0, ret, expr())
        ex(TokenType.SEMI)
        retstmt.len = cu().column - ret.column
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
                args.append(Params(type_tok, VariableNode(id_tok.line, id_tok.column, len(id_tok.String), id_tok.String, id_tok)))

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
        left = VariableNode(lefttok.line, lefttok.column, len(lefttok.String),lefttok.String, lefttok)
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
            case TokenType.MUT:
                return DeclarationNode(Typetok.line, Typetok.column, semi.column - semi.column + 1, left, right, type, VariableType.MUT)
            case TokenType.BORROW:
                return DeclarationNode(Typetok.line, Typetok.column, semi.column - semi.column + 1, left, right, type, VariableType.BORROW)
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
        順位,関数名（レベル）,演算子
        1,Primary / Postfix,"f()
        2,Unary / Prefix,"!, ~, -x, ++x, !!, ?!, %%!"
        3,Exponentiation,**
        4,Multiplicative,"*, /, //, %"
        5,Additive,"+, -, &",&
        6,Bitwise Shift,"<<, >>"
        7,Relational,"<, <=, >, >="
        8,Equality,"==, !=, ===, !==, <=>"
        9,Bitwise AND,& (単一)
        10,Bitwise XOR,^
        11,Bitwise OR,|
        12,Logical XOR,^^
        13,Logical AND,&&,
        14,Logical OR,||,
        15,Coalescing,"??, %%%, ?:"
        16,Range,..
        17,Assignment,"=, +=, ?= ..."
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
            return AssignNode(cus.line, cus.column, len(cus.String), nod, right, cus, AssginType[cus.type.name])
        return nod
    
    def Range() -> Expr:
        nod = Coalescing()
        if cu().type == TokenType.DOUBLEDOT:
            tok = ex(TokenType.DOUBLEDOT)
            right = Coalescing()
            if cu().type == TokenType.DOUBLEDOT:
                raise utils.ParseError("Range cannot be chained", cu().line, cu().column, source, "Range", cu().String)
            return BinaryOpNode(tok.line, tok.column, len(tok.String), nod, tok, right)
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
        return binary_op(Exponentiation, [TokenType.MULT, TokenType.DIV, TokenType.MOD])
    
    def Exponentiation() -> Expr:
        # まず左辺（Prefix）を読み込む
        nod = Prefix()
        
        # 次が ** だったら
        if cu().type == TokenType.EXP: # EXP = **
            tok = cu()
            ad()
            # 右辺として「自分自身」を呼ぶことで、右側の ** を先に処理させる
            right = Exponentiation()
            return BinaryOpNode(tok.line, tok.column, len(tok.String), nod, tok, right)
            
        return nod
    
    def Prefix() -> Expr:
        cus = cu()
        if cus.type in (TokenType.MULT, TokenType.ADD):
            ad()
            return UnaryOpNode(cus.line,cus.column, len(cus.String), cus, Prefix()) # 再帰して重ね掛け対応
        if cus.type == TokenType.BORROW:
            ad()
            return BorrowOpNode(cus.line, cus.column, len(cus.String), Prefix()) # 再帰で重ね掛け
        if cus.type == TokenType.MOVE:
            ad()
            return MoveOpNode(cus.line, cus.column, len(cus.String), Prefix()) # 再帰で重ね掛け
        return unary() # postfixへ

    def unary() -> Expr:
        cus = cu()
        if cus.type in (TokenType.LOGICNOT, TokenType.MINUS, TokenType.BITNOT):
            ad()
            return UnaryOpNode(cus.line,cus.column, len(cus.String), cus, unary()) # 再帰して重ね掛け対応
        return postfix() # postfixへ

    def postfix() -> Expr:
        node: Expr = prime() # まず核(123や変数名)を拾う

        while True:
            cus = cu("postfix")
            if cus.type == TokenType.DOT:
                ad()
                member = ex(TokenType.ID, "postfix")
                node = MemberAccessNode(cus.line,cus.column, len(cus.String), node, VariableNode(member.line, member.column, len(member.String), member.String, member))
            elif cus.type == TokenType.LBRACKET:
                ad()
                index = expr()
                ex(TokenType.RBRACKET)
                node = IndexAccessNode(cus.line,cus.column, len(cus.String), node, index)
            elif cus.type == TokenType.AS:
                ad()
                typeas = typenode()
                node = AsCastNode(cus.line, cus.column, len(cus.String), node, typeas)
            elif cus.type == TokenType.LPAREN:
                # primeの中にあった関数呼び出しロジックをここに移動！
                node = call_logic(node) 
            else:
                break
        return node
    
    def call_logic(node:Expr):
        # 関数呼び出し
        func = cu()
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
        end = cu()
        return CallExprNode(func.line, func.column, end.column - func.column, node, args)

    def prime() -> Expr:
        cus = cu("prime one")
        if (cus.type == TokenType.NUMBER):
            ad()
            if isinstance(cus.value, str|float):
                raise
            return NumberNode(cus.line,cus.column, len(cus.String), cus.value, cus, 10)
        elif (cus.type == TokenType.DECIMAL):
            ad()
            if isinstance(cus.value, str):
                raise
            return DecimalNode(cus.line,cus.column, len(cus.String), cus.value, cus)
        elif (cus.type == TokenType.ID):
            ad()
            if isinstance(cus.value, int|float):
                raise
            return VariableNode(cus.line,cus.column, len(cus.String), cus.value, cus)
        elif (cus.type == TokenType.LPAREN):
            ad()
            nod = expr()
            ex(TokenType.RPAREN, "prime", "it dont have ')' Token")
            return nod
        elif (cus.type == TokenType.TRUE):
            ad()
            return BoolNode(cus.line,cus.column, len(cus.String), cus, True)
        elif (cus.type == TokenType.FALSE):
            ad()
            return BoolNode(cus.line,cus.column, len(cus.String), cus, False)
        elif (cus.type == TokenType.NONE):
            ad()
            return NoneNode(cus.line,cus.column, len(cus.String), cus)
        elif (cus.type == TokenType.NULL):
            ad()
            return NullNode(cus.line,cus.column, len(cus.String), cus)
        elif (cus.type == TokenType.STR):
            ad()
            return StringNode(cus.line,cus.column, len(cus.String), cus.String, cus)
        raise utils.ParseError("unkonw Tokens",cus.line,cus.column,source,"prime", cus.String)
    nod = program(TokenType.END)
    return nod