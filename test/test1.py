
 

from llvmlite import ir

i32 = ir.IntType(32)

# 1. モジュールと関数の準備

module = ir.Module(name="list_example")

a = ir.GlobalVariable(
    module,
    i32,
    "a"
)

main_type = ir.FunctionType(i32, [])

main_func = ir.Function(module, main_type, name="main")

block = main_func.append_basic_block(name="entry")

builder = ir.IRBuilder(block)

alloca1 = builder.alloca(i32, name="test")

store = builder.store(ir.Constant(i32, 42), alloca1)

load1 = builder.load(alloca1, "load")

store = builder.store(ir.Constant(i32, 42), a)
add1 = builder.add(load1, load1, "add1")

# 終了処理 (return 0)

builder.ret(ir.Constant(i32, 0))


# --- 結果の表示 ---

print(module)
