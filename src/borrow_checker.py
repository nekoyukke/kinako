from copy import copy

from src.myast import *
from src.utils import AnalysisError
from src.tokens import *
from src.type import *
from src.myast import *
from src.parser import *
from src.tokens import *
from src.borrow import *

    
# 借用チェック
class BorrowingChecker:
    def __init__(self, node:Program, source:str) -> None:
        self.node = node
        self.source = source
        self._Scope = BorrowScope(source)

    def _util_CallError(self, message: str, node:Stmt|Expr) -> AnalysisError:
        raise AnalysisError(message, node.line, node.column, self.source, "", node.len)

    def _util_CallWarn(self, message: str, node:Stmt|Expr) -> None:
        print("警告" + AnalysisError(message, node.line, node.column, self.source, "", node.len).__str__())
    
    def visit_BorrowingChecker(self):
        return self._visit_Program(self.node)
    
    def _visit_Program(self, node:Program):
        for i in node.blocks:
            self._visit_Stmt(i)
        return
    
    def _util_None_kill(self, value:Symbol|None, node:Expr|Stmt):
        if value is None:
            raise self._util_CallError("Symbolがありません", node)
        return value
    
    def _util_None_kill_b(self, value:ResultBorrow | None, node:Expr|Stmt):
        if value is None:
            raise self._util_CallError("一時的に破棄される可能性があるオブジェクトは使用できません。", node)
        return value
    
    # STMTで回す
    def _visit_Stmt(self, node:Stmt):
        """
class DeclarationNode(Stmt):
class ExprStmtNode(Stmt):
class BlockNode(Stmt):
class IfStmtNode(Stmt):
class WhileStmtNode(Stmt):
class FunctionDefNode(Stmt):
class ReturnStmtNode(Stmt):
class ClassDefNode(Stmt):
class Program(Stmt):
class ForNode(Stmt):
class ImportNode(Stmt):
        """
        match (node):
            case DeclarationNode():
                return self._visit_Declaration(node)
            case ExprStmtNode():
                return self._visit_ExprStmt(node)
            case BlockNode():
                return self._visit_Block(node)
            case IfStmtNode():
                return self._visit_IfStmt(node)
            case WhileStmtNode():
                return self._visit_WhileStmt(node)
            case FunctionDefNode():
                return self._visit_FunctionDef(node)
            case ReturnStmtNode():
                return self._visit_ReturnStmt(node)
            case ForNode():
                return self._visit_ForStmt(node)
            case ImportNode():
                return self._visit_Import(node)
            case _:
                raise self._util_CallError(f"不明なnode '{node}'", node)
            
    def _visit_Declaration(self, node:DeclarationNode):
        pass

    def _visit_ExprStmt(self, node:ExprStmtNode):
        pass

    def _visit_Block(self, node:BlockNode):
        pass

    def _visit_IfStmt(self, node:IfStmtNode):
        pass
        
    def _visit_WhileStmt(self, node:WhileStmtNode):
        pass

    def _visit_FunctionDef(self, node:FunctionDefNode):
        pass

    def _visit_ReturnStmt(self, node:ReturnStmtNode):
        pass

    def _visit_ForStmt(self, node:ForNode):
        pass

    def _visit_Import(self, node:ImportNode):
        raise
    
    def _visit_expr(self, node:Expr) -> ResultBorrow | None:
        match(node):
            case BinaryOpNode():
                return self._visit_expr_binary(node)
            case VariableNode():
                return self._visit_expr_Variable(node)
            case Literal():
                return None
            case UnaryOpNode():
                return self._visit_expr_Unary(node)
            case AssignNode():
                return self._visit_expr_assign(node)
            case CallExprNode():
                return self._visit_expr_CallExpr(node)
            case MemberAccessNode():
                return self._visit_expr_Member(node)
            case IndexAccessNode():
                return self._visit_expr_Index(node)
            case AsCastNode():
                return self._visit_expr_AsCast(node)
            case MoveOpNode():
                return self._visit_expr_MoveOp(node)
            case BorrowOpNode():
                return self._visit_expr_BorrowOp(node)
            case ReferenceNode():
                return self._visit_expr_Reference(node)
            case DereferenceNode():
                return self._visit_expr_Dereference(node)
            case _:
                raise


    def _visit_expr_Variable(self, node:VariableNode) -> ResultBorrow:
        pass

    def _visit_expr_binary(self, node:BinaryOpNode) -> ResultBorrow | None:
        self._visit_expr(node.right)
        self._visit_expr(node.left)
        return None

    def _visit_expr_literal(self, node:Literal) -> ResultBorrow | None:
        return None

    def _visit_expr_Unary(self, node:UnaryOpNode) -> ResultBorrow | None:
        self._visit_expr(node)
        return None

    def _visit_expr_assign(self, node:AssignNode) -> ResultBorrow | None:
        pass

    def _visit_expr_CallExpr(self, node:CallExprNode) -> ResultBorrow | None:
        pass

    def _visit_expr_Member(self, node:MemberAccessNode) -> ResultBorrow | None:
        pass

    def _visit_expr_Index(self, node:IndexAccessNode) -> ResultBorrow | None:
        pass

    def _visit_expr_AsCast(self, node:AsCastNode) -> ResultBorrow | None:
        self._visit_expr(node)
        return None

    def _visit_expr_MoveOp(self, node:MoveOpNode) -> ResultBorrow | None:
        pass

    def _visit_expr_BorrowOp(self, node:BorrowOpNode) -> ResultBorrow | None:
        pass

    def _visit_expr_Reference(self, node:ReferenceNode) -> ResultBorrow | None:
        pass

    def _visit_expr_Dereference(self, node:DereferenceNode) -> ResultBorrow | None:
        pass