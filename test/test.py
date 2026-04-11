
 

from llvmlite import ir

 

# 1. モジュールと関数の準備

module = ir.Module(name="list_example")

main_type = ir.FunctionType(ir.IntType(32), [])

main_func = ir.Function(module, main_type, name="main")

block = main_func.append_basic_block(name="entry")

builder = ir.IRBuilder(block)

 

# --- 2. 構造体 (Node) の定義 ---

# 再帰的な構造体（自分自身へのポインタを持つ）を作るための特別な手順

node_type = module.context.get_identified_type("Node")

# 構造体の中身: { i32 (データ), Node* (次のノード) }

node_type.set_body(ir.IntType(32), node_type.as_pointer())

 

# --- 3. メモリ確保 (alloca) ---

# %node1 = alloca %Node

node1 = builder.alloca(node_type, name="node1")

# %node2 = alloca %Node

node2 = builder.alloca(node_type, name="node2")

 

# よく使う定数

int_0 = ir.Constant(ir.IntType(32), 0)

int_1 = ir.Constant(ir.IntType(32), 1)

data_10 = ir.Constant(ir.IntType(32), 10)

data_20 = ir.Constant(ir.IntType(32), 20)

null_ptr = ir.Constant(node_type.as_pointer(), None) # NULLポインタ
# --- 4. Node1 の設定 (Data: 10, Next: node2) ---

# データ部分へのアクセス (GEP)

# 引数: [ポインタ自体のオフセット(0), 構造体内のインデックス(0=data)]

ptr_data1 = builder.gep(node1, [int_0, int_0], name="ptr_data1")

builder.store(data_10, ptr_data1)

 

# 次のポインタ部分へのアクセス

# 引数: [ポインタ自体のオフセット(0), 構造体内のインデックス(1=next)]

ptr_next1 = builder.gep(node1, [int_0, int_1], name="ptr_next1")

builder.store(node2, ptr_next1) # node2のアドレスを入れる

 

# --- 5. Node2 の設定 (Data: 20, Next: NULL) ---

# データ部分

ptr_data2 = builder.gep(node2, [int_0, int_0], name="ptr_data2")

builder.store(data_20, ptr_data2)

 

# 次のポインタ部分

ptr_next2 = builder.gep(node2, [int_0, int_1], name="ptr_next2")

builder.store(null_ptr, ptr_next2) # NULLを入れる

 

# 終了処理 (return 0)

builder.ret(int_0)

 

# --- 結果の表示 ---

print(module)
