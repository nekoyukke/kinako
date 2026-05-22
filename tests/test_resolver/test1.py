from src.frontend.lexer.lexer import Lexer
from src.frontend.parser.parser import Parser
from src.frontend.collector.collector import Collector
from src.core.context.context import CompilationContext
from src.utils.error.error_lists import ErrorLists
from src.frontend.resolver.resolver import Resolver
## OK

source1 =\
"""
let int a = 1;
{
    let int a = 3;
    a = 3;
    {
        a = 555;
    }
}
"""

## DEAD
source2 =\
"""
let int a = 1;
{
    let int a = 3;
    a = 3;
    {
        b = 555;
    }
}
"""

## 進化したエラー

source3 =\
"""
let int foo = 1;
{
    let int bar = 3;
    foo = 3;
    {
        doo = 555; // realy->foo
    }
}
"""

## 絶対ちゃうやろ
source4 =\
"""
let int foo = 1;
{
    let int bar = 3;
    foo = 3;
    {
        sdiojgsduioghueisfjaoifhoifasduiauf = 555; // WTF????
    }
}
"""


def check(source:str):
    lex = Lexer(source)
    pas = Parser(lex.tokenize(), source)
    pro = pas.parse()
    context = CompilationContext()
    col = Collector(pro, source, context)
    col.collect()
    print(context)
    res = Resolver(pro, source, context)
    res.resolve()
    # print(pro)
    print(ErrorLists(pas.error))
    print(ErrorLists(col.error))
    print(ErrorLists(res.error))

check(source1)
check(source2)
check(source3)
check(source4)