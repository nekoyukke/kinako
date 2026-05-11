from typing import Any

from src.frontend.parser import Parser
from src.frontend.lexer import Lexer


def parse(source:str):
    pas = Parser[Any, Any](Lexer(source).tokenize(), source)
    print(pas.parse())
    for err in pas.error:
        print(err.__str__())

parse("""
if 1 1;
""")
print(Lexer("").REGEX)