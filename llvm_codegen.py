from ctypes import CFUNCTYPE, c_int


from llvmlite import binding as llvm
from llvmlite import ir
from myast import *
import tokens

class llvm_codegen:
    
    def __init__(self, node:list[ASTNode], filename:str = ""):
        # self.target = llvm.Target.from_default_triple()
        # self.target_machine = self.target.create_target_machine()

        self.module = ir.Module(filename)
        self.block = None
        self.func = None # 関数類
        self.funcsymbols = {}
        self.globalsymbols = {}
        self.localsymbols = {}
        self.builder = ir.IRBuilder(self.block)
        self.pos = 0
    
        self.node = node
        return
    
    def make_func(self, function:ir.Function):
        self.func = function
        self.make_block(self.func.append_basic_block(name = "entry"))
    
    def make_block(self, block:Optional[ir.Block]):
        self.block = block
        self.builder = ir.IRBuilder(self.block)
    
    def _test_make_func_obj(self, name:str):
        main_type = ir.FunctionType(ir.IntType(32), [])

        main_func = ir.Function(self.module, main_type, name="name")
        return main_func
    
    def visit(self, node:ASTNode):
        node_type = type(node).__name__
        method_name = f"visit_{node_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            # 未対応ノードなどの処理
            raise NotImplementedError(...)
    
    def isGlobal(self):
        return self.func is None
    
    def getvariable(self, name:str):
        pass
        
    def type_Conversion(self, node:ASTNode) -> ir.Type:
        if not isinstance(node, TypeNode):
            raise
        if isinstance(node, ListTypeNode):
            # irのlist等
            raise
        match (node.token.type):
            case tokens.TokenType.tINT:
                return ir.IntType(32) # type: ignore
            
            case tokens.TokenType.tINT8:
                return ir.IntType(8) # type: ignore
            
            case tokens.TokenType.tINT16:
                return ir.IntType(16) # type: ignore
            
            case tokens.TokenType.tINT32:
                return ir.IntType(32) # type: ignore
            
            case tokens.TokenType.tINT64:
                return ir.IntType(64) # type: ignore
            
            case tokens.TokenType.tINT128:
                return ir.IntType(128) # type: ignore
            
            case tokens.TokenType.tFLOAT:
                return ir.FloatType()
            
            case tokens.TokenType.tDOUBLE:
                return ir.DoubleType()

            case tokens.TokenType.tFLOAT32:
                return ir.FloatType()

            case tokens.TokenType.tFLOAT64:
                return ir.DoubleType()
            
            case _:
                raise
    
    def visit_ExprStmtNode(self, node:ASTNode):
        if not isinstance(node, ExprStmtNode):
            raise
        self.Analysis(node.expr, ir.IntType(32))

    def visit_DeclarationNode(self, node:ASTNode):
        if not isinstance(node, DeclarationNode):
            raise
        if self.isGlobal():
            res = ir.GlobalVariable(
                self.module,
                self.type_Conversion(node.type),
                node.left.name
            )
            self.util_set_variable(res)
        else:
            res = self.builder.alloca(
                self.module,
                self.type_Conversion(node.type),
                node.left.name,
            )
            self.util_set_variable(res)
        return

    def Analysis(self, node:Expr, type:ir.Type):
        # 何を返すか
        match (node):
            case NumberNode():
                # 数字
                return ir.Constant(
                    type,
                    node.value
                )
            case BoolNode():
                # 真偽値
                return ir.Constant(
                    type,
                    int(node.flag)
                )
            case NullNode():
                # null(void*0), (いい感じの型*0)
                return ir.Constant(
                    None,
                    None
                )
            case NoneNode():
                # いい感じの無効値
                # Todo::解析系からとってくる
                return ir.Constant(
                    None,
                    None
                )
            case VariableNode():
                # 変数
                res = self.builder.load(
                    self.get_variable(node.name),
                    f"{self.pos}"
                )
                self.pos += 1
                return res
            case CallExprNode():
                # 引数を再帰的に渡して返り値
                raise
            case StringNode():
                # 文字列
                # グローバル
                raise
            case BinaryOpNode():
                # 2項演算
                l = self.Analysis(node.left, type)
                r = self.Analysis(node.right, type)
                print(l,r)
                match(node.op.type):
                    case tokens.TokenType.ADD:
                        res = self.builder.add(
                            l,
                            r,
                            f"{self.pos}"
                        )
                        self.pos += 1
                        return res
                    case tokens.TokenType.MINUS:
                        res = self.builder.sub(
                            l,
                            r,
                            f"{self.pos}"
                        )
                        self.pos += 1
                        return res
                    case tokens.TokenType.MULT:
                        res = self.builder.mul(
                            l,
                            r,
                            f"{self.pos}"
                        )
                        self.pos += 1
                        return res
                    case tokens.TokenType.DIV:
                        res = self.builder.sdiv(
                            l,
                            r,
                            f"{self.pos}"
                        )
                        self.pos += 1
                        return res
                    case _:
                        raise
            case UnaryOpNode():
                # 単項演算
                raise
            case LogicalOpNode():
                # logic演算
                raise
            case AssginNode():
                # 代入！
                raise
            case MemberAccessNode():
                # メンバアクセス
                raise
            case IndexAccessNode():
                # インデックス
                raise
            case _:
                raise

if __name__ == "__main__":
    nodes:list[ASTNode] = [
        ExprStmtNode(
            0,0,0,
            BinaryOpNode(
                0,0,0,
                NumberNode(
                    0,0,0,10,Token(tokens.TokenType.ID, 10,),
                    10
                ),
                Token(tokens.TokenType.ADD, "ADD")
                ,
                NumberNode(
                    0,0,0,20,Token(tokens.TokenType.ID, 10,),
                    10
                )
            )
        )
    ]
    ll = llvm_codegen(nodes)
    ll.make_func(ll._test_make_func_obj("main"))
    print(ll.visit(nodes[0]))
    print(ll.module)