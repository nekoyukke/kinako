from tests.util import *
source = """
a();
"""
a = Parser(
Lexer(source).tokenize(), source 
)
from src.frontend.parser.models.stmt import ExprStmt

print(*Lexer(source).tokenize(),sep="\n")

print(a._Stmt_entry()) # type: ignore
a.pos=0;a.error=[]
try:
    print(a.peek())
    expr = a._expr_entry() # type: ignore
    a.consume(TokenType.SEMI, "セミコロンがありません！")
    print(ExprStmt(expr.line, expr.col, expr.len, expr))
except KinakoSyntaxError: 
    a.synchronize()
print(ErrorLists(a.error).__str__())
# 原因:
# postfixでmatchしてたくせに_finish_callでconsumeしてた