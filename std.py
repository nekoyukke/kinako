from myast import *
from tokens import *

STD:dict[str, dict[str, dict[str, Symbol]]] = {
    "std": {
        "io": {
            "print": Symbol(
                "print",
                "std.io.print",
                FunctionDefNode(
                    0,0,0,Token.zero(),
                    Stmt(),FunctionTypeNode(
                        "Function",
                        Token.zero(),
                        False,
                        [
                            TypeNode(
                                "String",
                                Token(TokenType.tSTR,0),
                                False
                            ),
                        ],
                        None
                    ),
                    [Params(
                        TypeNode(
                            "String",
                            Token(TokenType.tSTR,0),
                            False
                        ),
                        VariableNode("s", Token.zero())
                    )]
                )
            ),
            # "println": Symbol(...),
            # "File": Symbol(...),
        },
        "math": {
            # "sin": Symbol(...),
            # "cos": Symbol(...),
        }
    }
}