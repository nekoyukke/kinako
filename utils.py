import logging
"""
デバッグ便利コード用
フラグがTrueならINFO以下も表示
"""
FLAG=True
if FLAG:
    logging.basicConfig(
        level=logging.DEBUG,                # ログレベル（DEBUG 以上を表示）
        format="%(asctime)s  [%(levelname)s]:%(message)s ",  # 出力フォーマット
    )
else:
    logging.basicConfig(
        level=logging.INFO,                # ログレベル（DEBUG 以上を表示）
        format="%(asctime)s  [%(levelname)s]:%(message)s ",  # 出力フォーマット
    )
class ParseError(Exception):
    def __init__(self, message: str, line: int, column: int, source: str, name: str, tok:str) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        self.name = name
        self.tok = tok
        super().__init__(self.__str__())

    def __str__(self) -> str:
        # 行テキストを抽出
        line_text = self.source.splitlines()[self.line - 1]
        # カーソル位置に ^ を置く
        pointer = " " * (self.column - 1) + "^" * len(self.tok)
        return (
            f'\nTraceback: {self.name}'
            f'\n  File "<source>", line {self.line}\n'
            f"    {line_text}\n"
            f"    {pointer}\n"
            f"ParseError ParseRuntimeError!: {self.message}"
        )
    
class AnalysisError(Exception):
    def __init__(self, message: str, line: int, column: int, source: str, name: str, len:int) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        self.name = name
        self.len = len
        super().__init__(self.__str__())

    def __str__(self) -> str:
        # 行テキストを抽出
        line_text = self.source.splitlines()[self.line - 1]
        # カーソル位置に ^ を置く
        pointer = " " * (self.column - 1) + "^" * self.len
        return (
            f'\nTraceback: {self.name}'
            f'\n  File "<source>", line {self.line}\n'
            f"    {line_text}\n"
            f"    {pointer}\n"
            f"AnalysisError AnalysisRuntimeError!: {self.message}"
        )
