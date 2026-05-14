from dataclasses import dataclass
from frontend.lexer.tokentype import TokenType

@dataclass
class Token():
    type: TokenType
    value: str
    line: int
    column: int
    len: int