from ctypes import CFUNCTYPE, c_int


from llvmlite import binding as llvm
from llvmlite import ir
from myast import *
import tokens

class llvm_codegen:
    
    def __init__(self, node:list[ASTNode], filename:str = ""):
        self.target = llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()

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
        
    def visit_DeclarationNode(self, node:ASTNode):
        if not isinstance(node, DeclarationNode):
            raise
        if self.isGlobal():
            ir.GlobalVariable(
                self.module,
                self.type_Conversion(node.type),
                node.,
            )
        else:
            ir.GlobalVariable(
                self.module,
                self.type_Conversion(node.type),
                node.Declarationname,
            )
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
                self.builder.load(
                    self.getvariable(node.name),
                    f"{self.pos}"
                )
                return f"{self.pos}"
            case FunctionNode():
                # 関数のポインタ
            case CallExprNode():
                # 引数を再帰的に渡して返り値
            case StringNode():
                # 文字列
                # グローバル
            case BinaryOpNode():
                # 2項演算
            case UnaryOpNode():
                # 単項演算
            case LogicalOpNode():
                # logic演算
            case AssginNode():
                # 代入！
            case MemberAccessNode():
                # メンバアクセス
            case IndexAccessNode():
                # インデックス