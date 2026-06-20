from src.core.source.source_span import SourceSpan


def display_span(source:str, spans: list[tuple[str, SourceSpan]]):
    for s in spans:
        print(s[0] + ":" + _extract_error_line(source, s[1].line, s[1].col, s[1].len))

def _extract_error_line(source_code: str, line: int, col: int, length: int) -> str:
    """
    指定された行(1始まり)、列(0始まり)、長さから該当する行を抜き出し、
    エラー位置をカーソル(^)で指し示す文字列を返します。
    """
    # ソースコードを行ごとに分割
    lines = source_code.splitlines()
    
    # 行番号は通常1始まりなので、インデックス(0始まり)に変換
    line_idx = line - 1
    
    # 指定された行がソースコードの範囲内かチェック
    if line_idx < 0 or line_idx >= len(lines):
        return "Error: Location out of range"
        
    # 該当する行を取得
    target_line = lines[line_idx]
    
    # エラー箇所を指し示すアンダーライン（^）を作成
    # 列（col）までのスペース + 長さ（length）分の '^'
    indicator = " " * col + "^" * length
    
    # 該当行とインジケータを結合して返す
    return f"{target_line}\n{indicator}"
