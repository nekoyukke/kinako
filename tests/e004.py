from tests.util import *

import ctypes

def get_object_by_id(obj_id: int) -> Any:
    """指定されたオブジェクトID（メモリ番地）から元のオブジェクトを取得します"""
    return ctypes.cast(obj_id, ctypes.py_object).value


source = """
fn main() -> int {
    let a:int = 1;

    {
        return a;
    }
}
"""

program = parser(source)
ctx = builtin()
collector(source, program, context=ctx)
resolver(source, program, ctx,)

print(ctx)

from src.utils.display.span_display import display_span
spans:list[tuple[str, SourceSpan]] = []
for k,v in ctx.resolved.items():
    if isinstance(v, VariableSymbol):
        spans.append((f"{v}\n\n", get_object_by_id(k)))
display_span(source, spans)