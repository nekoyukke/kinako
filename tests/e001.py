from tests.util import *

source = """
fn main() -> int {
    let x:int = add(3,3);
    return 0;
}

fn add(a: int, b: int) -> int {
    return a + b;
}
"""

program = parser(source)
ctx = builtin()
collector(source, program, context=ctx)
resolver(source, program, ctx,)

print(ctx)