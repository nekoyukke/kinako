from dataclasses import dataclass
from src.frontend.models.tokentype import TokenType

@dataclass
class Token():
    type: TokenType
    value: str
    line: int
    column: int
    len: int