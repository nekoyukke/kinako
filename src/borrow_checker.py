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
    
    def marge_scope(self, scope1:BorrowScope, scope2:BorrowScope, node:Stmt):
        map1 = scope1.map
        map2 = scope2.map
        result = self._Scope
        all_places = set(map1.keys()) | set(map2.keys())
        for p in all_places:
            state_a = scope1.get_map(p)
            state_b = scope2.get_map(p)
            if not state_a or not state_b:
                continue
                raise RuntimeError("不明なエラーです。Issueして")
            new_static = self._merge_static(state_a, state_b, node)
            result.map[p] = new_static
        return result
    
    def _merge_static(self, state1:StaticBorrow, state2:StaticBorrow, node:Stmt):
        state = self._merge_state(state1.state, state2.state, node)
        if state1.vt != state2.vt:
            raise self._util_CallError(f"マージ結果が違反です。{state1}と{state2}", node)
        vt = state1.vt
        if state1.ref_count != state2.ref_count:
            raise self._util_CallError(f"マージ結果が違反です。{state1}と{state2}", node)
        ref_count = state1.ref_count
        if state1.have != state2.have:
            raise self._util_CallError(f"マージ結果が違反です。{state1}と{state2}", node)
        have = state1.have
        return StaticBorrow(state, vt, have, ref_count)


    def _merge_state(self, state1:BorrowState, state2:BorrowState, node:Stmt):
        if state1 == state2:
            return state1
        if state1 == BorrowState.ACTIV and state2 == BorrowState.UNINITIALIZED:
            return BorrowState.UNINITIALIZED
        if state2 == BorrowState.ACTIV and state1 == BorrowState.UNINITIALIZED:
            return BorrowState.UNINITIALIZED
        raise self._util_CallError(f"マージ結果が違反です。{state1}と{state2}", node)

    # STMTで回す
    def _visit_Stmt(self, node:Stmt) -> BorrowScope:
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
            
    def _visit_Declaration(self, node:DeclarationNode) -> BorrowScope:
        sym = self._util_None_kill(node.symbol, node)
        if node.right is not None:
            right = self._visit_expr(node.right)
            # もしBORROWなら左が正しいか見る
            if node.vartype == VariableType.BORROW:
                right = self._util_None_kill_b(right, node)
                if right.state != BorrowState.BORROW:
                    # あうと
                    raise self._util_CallError(f"BORROW束縛は '{right.state}' は不可です。", node)
                self._Scope.add_map(Place.make(sym), StaticBorrow(BorrowState.ACTIV, node.vartype, right.have))
                return self._Scope
            # それ以外でもおっけーです！
            self._Scope.add_map(Place.make(sym), StaticBorrow(BorrowState.ACTIV, node.vartype, None))
            return self._Scope
        if node.vartype in (VariableType.BORROW, VariableType.CONST, VariableType.VAL):
            raise self._util_CallError("初期値がありません。", node)
        # 異状なし
        self._Scope.add_map(Place.make(sym), StaticBorrow(BorrowState.ACTIV, node.vartype, None))
        return self._Scope

    def _visit_ExprStmt(self, node:ExprStmtNode) -> BorrowScope:
        self._visit_expr(node.expr)
        return self._Scope

    def _visit_Block(self, node:BlockNode) -> BorrowScope:
        self._Scope = self._Scope.new_scope()

        # 回す
        for stmt in node.blocks:
            self._visit_Stmt(stmt)
        scope = self._Scope

        self._Scope = self._Scope.cloce_scope()
        return scope

    def _visit_IfStmt(self, node:IfStmtNode) -> BorrowScope:
        self._visit_expr(node.condition)
        scope = copy(self._Scope)
        self._visit_Stmt(node.then_block)
        scope1 = copy(self._Scope)
        self._Scope = copy(scope)
        if node.else_block:
            self._visit_Stmt(node.else_block)
            scope2 = copy(self._Scope)
        else:
            scope2 = copy(scope)
        self._Scope = self.marge_scope(scope1, scope2, node)
        return self._Scope
        
    def _visit_WhileStmt(self, node:WhileStmtNode) -> BorrowScope:
        self._visit_expr(node.condition)

        
        self._visit_Stmt(node.body)

    def _visit_FunctionDef(self, node:FunctionDefNode) -> BorrowScope:
        pass

    def _visit_ReturnStmt(self, node:ReturnStmtNode) -> BorrowScope:
        pass

    def _visit_ForStmt(self, node:ForNode) -> BorrowScope:
        pass

    def _visit_Import(self, node:ImportNode) -> BorrowScope:
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
        sym = self._util_None_kill(node.symbol, node)
        static = self._Scope.get_map(Place.make(sym))
        if static is None:
            raise self._util_CallError(f"不明な変数 '{sym.name}' 不明な値は使用できません。\n{self._Scope.map[Place.make(sym)]}", node)
        return ResultBorrow(ResultState.OWNED, Place.make(sym), static.state)

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
        left = self._visit_expr(node.left)
        left = self._util_None_kill_b(left, node)
        if left.state in (BorrowState.BORROW, BorrowState.BORROWED, BorrowState.MOVED, ):
            raise self._util_CallError("有効値ではありません！", node)
        sb = self._Scope.get_map(left.have)
        if sb is None:
            raise self._util_CallError("不明な左辺", node)
        if sb.vt in (VariableType.BORROW, VariableType.CONST, VariableType.VAL):
            raise self._util_CallError("左辺は変更不可能な束縛によって制御されているため、制御ができません", node)
        return self._visit_expr(node.right)

    def _visit_expr_CallExpr(self, node:CallExprNode) -> ResultBorrow | None:
        pass

    def _visit_expr_Member(self, node:MemberAccessNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node)
        borrow = self._util_None_kill_b(borrow, node)
        symbol = node.right.symbol
        symbol = self._util_None_kill(symbol, node)
        result = borrow.add_projection(Projection(ProjectionKind.FIELD, symbol))
        return result

    def _visit_expr_Index(self, node:IndexAccessNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node)
        borrow = self._util_None_kill_b(borrow, node)
        result = borrow.add_projection(Projection(ProjectionKind.INDEX, None))
        return result

    def _visit_expr_AsCast(self, node:AsCastNode) -> ResultBorrow | None:
        self._visit_expr(node)
        return None

    def _visit_expr_MoveOp(self, node:MoveOpNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node.right)
        borrow = self._util_None_kill_b(borrow, node)
        sb = self._Scope.get_map(borrow.have)
        if sb is None:
            raise
        if sb.state in (BorrowState.BORROW, BorrowState.MOVED):
            raise self._util_CallError("moveは所有権が完全では無ければなりません。", node)
        sb.state = BorrowState.MOVED
        return ResultBorrow(ResultState.OWNED, borrow.have, BorrowState.MOVED)

    def _visit_expr_BorrowOp(self, node:BorrowOpNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node.right)
        borrow = self._util_None_kill_b(borrow, node)
        sb = self._Scope.get_map(borrow.have)
        if sb is None:
            raise
        if sb.vt != VariableType.MUT:
            raise self._util_CallError("borrowはmutのみが許されます", node)
        if sb.state in (BorrowState.BORROW, BorrowState.MOVED):
            raise self._util_CallError("borrowは所有権が完全では無ければなりません。", node)
        self._Scope.add_ref(borrow.have)
        return ResultBorrow(ResultState.BORROWED, borrow.have, BorrowState.BORROW)

    def _visit_expr_Reference(self, node:ReferenceNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node.right)
        borrow = self._util_None_kill_b(borrow, node)
        sb = self._Scope.get_map(borrow.have)
        if sb is None:
            raise
        if sb.vt != VariableType.LET:
            raise self._util_CallError("&はletのみが許されます", node)
        return ResultBorrow(ResultState.BORROWED, borrow.have, BorrowState.ACTIV)

    def _visit_expr_Dereference(self, node:DereferenceNode) -> ResultBorrow | None:
        borrow = self._visit_expr(node.right)
        borrow = self._util_None_kill_b(borrow, node)
        sb = self._Scope.get_map(borrow.have)
        if sb is None:
            raise
        if sb.vt != VariableType.LET:
            raise self._util_CallError("&はletのみが許されます", node)
        place = borrow.have.add_projection(Projection(ProjectionKind.DEREF, None))
        data = self._Scope.get_map(place)
        if data is None:
            raise
        return ResultBorrow(ResultState.OWNED, place, data.state)