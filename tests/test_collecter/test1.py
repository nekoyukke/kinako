from src.frontend.lexer.lexer import Lexer
from src.frontend.parser.parser import Parser
from src.frontend.collector.collector import Collector
from src.core.context.context import CompilationContext
from src.utils.error.error_lists import ErrorLists
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

## OK
source3 =\
"""

fn let int add(let int a, let int b) {
    return a + b;
}

fn let int main() {
    return 0;
}
"""

## NG

source4 =\
"""

fn let int add(let int a, let int b) {
    let int a = 1;
    return a + b;
}

fn let int main() {
    return 0;
}
"""

## DOUBLE NG

source5 =\
"""
fn let int add(let int a, let int b) {
    let int a = 1;
    return a + b;
}
fn let int main() {
    let int foo = 1;
    let int foo = 1;
    return 0;
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
    print(ErrorLists(pas.error))
    print(ErrorLists(col.error))

check(source1)
check(source2)
check(source3)
check(source4)
check(source5)