from src.frontend.lexer.lexer import Lexer
from src.frontend.parser.parser import Parser
from src.frontend.collector.collector import Collector
from src.core.context.context import CompilationContext

## OK

source1 =\
"""
let int a = 1;
{
    let int a = 3;
}
"""

## OUT

source2 =\
"""
let int a = 1;
{
    let int a = 3;
    let int a = 3;
}
"""

def check(source:str):
    lex = Lexer(source)
    pas = Parser(lex.tokenize(), source)
    pro = pas.parse()
    context = CompilationContext()
    col = Collector(pro, source, context)
    col.collect()
    # print(pro)
    print(context)
    for err in pas.error:
        print(err.__str__())
    for err in col.error:
        print(err.__str__())

check(source1)
check(source2)