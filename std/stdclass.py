from myast import *
from tokens import *
from type import *

def make_std_class(Type:TypeObject) -> list[Symbol] | None:
    if Type == TypeInt(32, False, True):
        return [
                Symbol(
                "ToString",
                "Int32.ToString",
                FunctionDefNode(
                    0,0,0,Token.zero(),
                    Stmt(0,0,0),FunctionTypeNode(
                        "Function",
                        Token.zero(),
                        False,
                        [
                        ],
                        None
                    ),
                    []
                ),
                is_extern=True,
                Type_analysis=TypeFunction([], TypeString())
                ),
            ]
    # ふめい
    return None