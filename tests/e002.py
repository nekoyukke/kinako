from tests.util import *

source = """
fn main() -> int {
    let a:int = 1;
    let b:int = a;

    return b;
}
"""

program = parser(source)
ctx = builtin()
collector(source, program, context=ctx)
resolver(source, program, ctx,)

print(ctx)