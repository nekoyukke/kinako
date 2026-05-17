from src.frontend.lexer.lexer import Lexer
from src.frontend.parser.parser import Parser


## このコードでどの部分でエラーができるか
# もしlet int a = ;の部分でエラーが出て、内部が完全にパースしきれないならエラー

source =\
"""
let int a = 1;
{
    let int a = ;
    a = a;
    a = a + b;
    anchor {
        ahokusa;
    }
}
"""

lex = Lexer(source)
pas = Parser(lex.tokenize(), source)
print(pas.parse())
for err in pas.error:
    print(err.__str__())