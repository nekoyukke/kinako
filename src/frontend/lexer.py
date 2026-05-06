import re

from src.frontend.models.token import Token
from src.frontend.models.tokentype import TokenType

class Lexer():
    def __init__(self, source:str) -> None:
        self.source = source
        self.REGEX = self.build_regex()

    def build_regex(self):
        # 記号や演算子（正規表現を持つもの）を抽出
        # 文字数が長い順にソートして、=== が == より先にくるようにする
        patterns:list[str] = []
        for t in TokenType:
            # 文字列リテラル（キーワード）ではなく、正規表現っぽいものを判別
            # あるいは単純に全メンバーを対象にしてもOK
            patterns.append(f'(?P<{t.name}>{t.value})')

        return re.compile('|'.join(patterns))


    def tokenize(self) -> list[Token]:
        line = 0
        col = 0
        tokens:list[Token] = []
        for mo in self.REGEX.finditer(self.source):
            kind_name = mo.lastgroup
            value = mo.group()
            start = mo.start()
            line = self.source.count("\n", 0, start) + 1
            col = start - self.source.rfind("\n", 0, start)
            if kind_name is None:
                raise
        
            # kind_name (Enumの名前) から直接 Enumオブジェクトを取得
            kind = TokenType[kind_name]
        
            match (kind):
                case TokenType.SKIP:
                    continue
                case _:
                    # Token生成
                    tokens.append(Token(kind, value, line, col, len(value)))
        tokens.append(Token(TokenType.EOF, "", 0,0,0,))
        return tokens

if __name__ == "__main__":
    lex = Lexer("let int a = 1;")
    lex.tokenize()