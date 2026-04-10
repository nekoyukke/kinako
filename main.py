from lexer import tokenize
from tokens import Token
from myast import *
from parser import *
from analysis import *

import logging
import utils  # type: ignore
# from interpreter import evaluate
# from environment import Environment

def run_source(source: str) -> None:
    """
    ソースコードを実行する
    """
    logging.debug(f"Tokens::")
    tokens: list[Token] = tokenize(source)
    for t in tokens:
        logging.debug(f"Token: {t}")
    node = ast(tokens, source)
    sc = ScopeChecker(node, source)
    sc.reset()
    print("sccheck")
    print(sc.visit_Scope_Check().__repr__())
    tc = TypeChecker(node, source)
    print("tccheck")
    print(tc.visit_TypeCheck())
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            print(run_source(f.read()))
    else:
        while True:
            line = input(">>> ")
            print(run_source(line))
            """try:
                line = input(">>> ")
                print(run_source(line))
            except Exception as e:
                print("Error:", e)"""