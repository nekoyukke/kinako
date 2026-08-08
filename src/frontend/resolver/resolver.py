import difflib

import src.core.context.context as _ctx
from src.core.symbol.symbol import Symbol
from src.core.source.source_span import SourceSpan

import src.core.ast.stmt as _stmt
import src.core.ast.expr as _expr
import src.core.ast.base as _base
from src.utils.error.resolver import KinakoResolverError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo, KinakoBaseError
from src.core.scope.scope import Scope
from src.core.context.id import *

from src.core.contract.policy.policy import Policy, Policy_Union, Policy_Generic
from src.core.contract.right.right import Right, Right_Union, Right_Generic
import src.core.contract.type.type as _t
from src.core.variable.variable import VariableDef
from src.core.function.function import FunctionDef



class Resolver:
    def __init__(self, program:_stmt.ProgramStmt, source: str, context:_ctx.Context) -> None:
        self.program = program
        self.context = context
        self.source = source
        self.error:list[KinakoBaseError] = []
        self.scope = Scope(None, {})
    
    def resolve(self):
        # トップレベルに限らず、すべての定義を参照。
        return self._visit_program()

    def call_error(self, message:str, node:_base.ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoResolverError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
    
    def push_scope(self):
        self.scope = Scope(self.scope, {})

    def pop_scope(self, node:_base.ASTNode):
        if self.scope.parent is None:
            self.call_error(f"kinakoコンパイラーエラー不明なスコープ取引、デバッグ情報:{self.scope.symbols}", node)
            raise
        self.scope = self.scope.parent

    def resolve_contract(self, contract:_base.Contract, err_node:_base.ASTNode):
        if contract.type:contract.type_id = self.resolve_type_identifier(contract.type)
        else:
            if  in self.context.types
        if contract.right:contract.right_id = self.resolve_right_identifier(contract.right)
        if contract.policy:contract.policy_id = self.resolve_policy_identifier(contract.policy)
        
    def resolve_type_identifier(self, contract:_base.Identifier) -> TypeId:
        if isinstance(contract, _base.Real_Identifier):
            # ビルドイン
            if contract.name in self.context.buildin_type:
                return self.context.buildin_type[contract.name]
            # ユーザ定義型
            raise
        elif isinstance(contract, _base.Union_Identifier):
            type = self.resolve_type_identifier(contract.identifiers[0])

            for i in contract.identifiers[1:]:
                left = self.resolve_type_identifier(i)
                # T | Tの場合
                if type == left:
                    continue
                type_real = _t.UnionType(type, left)
                # すでにcontextにあった場合
                if type_real in self.context.types:
                    type = TypeId(self.context.types.index(type_real))
                    continue
                # contextに追加して更新
                self.context.types.append(type_real)
                type = TypeId(len(self.context.types) - 1)
            return type
        elif isinstance(contract, _base.Generic_Identifier):
            # ジェネリック
            # 今のところジェネリックは組み込みしかないので、ベタな実装をする
            # contract.expr こっちが中
            # contract.generic こっちが外
            expr = self.resolve_type_identifier(contract.expr)
            generic = self.resolve_type_identifier(contract.generic)
            # 外だけはんていちゅ
            generic_real = self.context.types[generic.value]
            if isinstance(generic_real, _t.ArrayType):
                self.context.types.append(_t.ArrayType(expr, 0)) # メンバ追加するの忘れた。list[ide...]にするべき。あと、構文、"Number_Identifier"を追加
                return TypeId(len(self.context.types)-1)
            elif isinstance(generic_real, _t.PtrType):
                self.context.types.append(_t.PtrType(expr))
                return TypeId(len(self.context.types)-1)
            else:
                raise
        raise
        
    def resolve_right_identifier(self, contract:_base.Identifier) -> Right:
        if isinstance(contract, _base.Real_Identifier):
            return self.context.right[contract.name]
        elif isinstance(contract, _base.Union_Identifier):
            right = self.resolve_right_identifier(contract.identifiers[0])
            for i in contract.identifiers[1:]:
                right = Right_Union(right, self.resolve_right_identifier(i))
            return right
        elif isinstance(contract, _base.Generic_Identifier):
            return Right_Generic(self.resolve_right_identifier(contract.generic), self.resolve_right_identifier(contract.expr))
        raise
        
    def resolve_policy_identifier(self, contract:_base.Identifier) -> Policy:
        if isinstance(contract, _base.Real_Identifier):
            return self.context.policy[contract.name]
        elif isinstance(contract, _base.Union_Identifier):
            right = self.resolve_policy_identifier(contract.identifiers[0])
            for i in contract.identifiers[1:]:
                right = Policy_Union(right, self.resolve_policy_identifier(i))
            return right
        elif isinstance(contract, _base.Generic_Identifier):
            return Policy_Generic(self.resolve_policy_identifier(contract.generic), self.resolve_policy_identifier(contract.expr))
        raise

    
    def get_names(self, name:str, cc:int=1) -> list[str]:
        names:list[str] = []
        names += list(self.context.policy)
        names += list(self.context.right)
        names += self.scope.get_variable()
        return difflib.get_close_matches(name, names, cc)

    def _get_node_id(self, ast: _base.ASTNode):
        return id(ast)

    def _visit_program(self):
        for s in self.program.instr:
            self._visit_try_stmt(s)
    
    def _visit_try_stmt(self, node:_stmt.Stmt):
        self._visit_stmt(node)
    
    def _visit_stmt(self, node:_stmt.Stmt):
        match (node):
            case _stmt.VariableDeclStmt():
                if node.left:
                    self._visit_expr(node.left)

                name = node.name.ident
                if self.scope.check(name):
                    other = self.scope.lookup(name)
                    if other is not None:
                        other_symbol = self.context.symbols[other.value]
                        match(other_symbol.entity):
                            case VariableId():
                                other_value = self.context.variables[other_symbol.entity.value]
                                span = other_value.span
                                self.call_error("宣言がかぶっています。", node, related=[KinakoRelatedInfo("被っている宣言元:", span.line, span.col, span.len)])
                                return
                            case FunctionId():
                                other_value = self.context.functions[other_symbol.entity.value]
                                span = other_value.span
                                self.call_error("宣言がかぶっています。", node, related=[KinakoRelatedInfo("被っている宣言元:", span.line, span.col, span.len)])
                                return
                            case _:
                                self.call_error("宣言がかぶっています。", node)
                                return
                    else:
                        self.call_error("宣言がかぶっています。", node)
                        return
                    raise
                self.resolve_contract(node.contract, node)
                symid: SymbolId = SymbolId(len(self.context.symbols))
                var:VariableId = VariableId(len(self.context.variables))
                self.context.variables.append(
                    VariableDef(
                        symid,
                        node.contract.type_id,
                        node.contract.right_id,
                        node.contract.policy_id,
                        SourceSpan(node.line, node.col, node.len)
                    )
                )
                self.context.symbols.append(
                    Symbol(
                        symid,
                        name,
                        var,
                        SourceSpan(node.line, node.col, node.len)
                    )
                )
                self.scope.define(
                    name,
                    symid
                )
                node.symbolid = symid
                return
            case _stmt.FunctionDeclStmt():
                name:str = node.name.ident
                self.resolve_contract(node.result, node)
                symid: SymbolId = SymbolId(len(self.context.symbols))
                var:VariableId = VariableId(len(self.context.variables))
                self.context.variables.append(
                    VariableDef(
                        symid,
                        node.result.type_id,
                        node.result.right_id,
                        node.result.policy_id,
                        SourceSpan(node.line, node.col, node.len)
                    )
                )
                self.context.symbols.append(
                    Symbol(
                        symid,
                        name,
                        var,
                        SourceSpan(node.line, node.col, node.len)
                    )
                )
                self.scope.define(
                    name,
                    symid
                )
                node.symbolid = symid
                self.push_scope()

                for i in node.params:
                    name = i.name
                    self.resolve_contract(i.contract, node)
                    symid: SymbolId = SymbolId(len(self.context.symbols))
                    var:VariableId = VariableId(len(self.context.variables))
                    self.context.variables.append(
                        VariableDef(
                            symid,
                            i.contract.type_id,
                            i.contract.right_id,
                            i.contract.policy_id,
                            SourceSpan(node.line, node.col, node.len)
                        )
                    )
                    self.context.symbols.append(
                        Symbol(
                            symid,
                            name,
                            var,
                            SourceSpan(node.line, node.col, node.len)
                        )
                    )
                    self.scope.define(
                        name,
                        symid
                    )
                    i.symbol = symid
                self._visit_stmt(node.body)

                self.pop_scope(node)
                return
            case _:
                flag = isinstance(node, _stmt.BlockStmt | _stmt.Ifstmt | _stmt.WhileStmt | _stmt.ForEachStmt)
                if flag:
                    self.push_scope()
                nodes = node.get_child()
                for i in nodes:
                    if isinstance(i, _expr.Expr):
                        self._visit_expr(i)
                    elif isinstance(i, _stmt.Stmt):
                        self._visit_try_stmt(i)
                if flag:
                    self.pop_scope(node)
                return
            

    def _visit_expr(self, node:_expr.Expr):
        match (node):
            case _expr.Variable():
                # セット
                lookup = self.scope.lookup(node.ident.name)
                if lookup:
                    lookup.name
                    self.context.resolved[self._get_node_id(node)] = lookup
                    return
                if node.ident.name in self.context.functions:
                    # チェックはあっち側。
                    return
                name = self.get_names(node.ident.name)
                if name:
                    if name[0] in self.scope.get_variable():
                        other = self.scope.lookup(name[0])
                        if other is not None:
                            self.call_error(f"不明な変数名{node.ident}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", other.span.line, other.span.col, other.span.len)])
                        elif node.ident in self.context.functions:
                            span = self.context.functions[node.symbolid.value].span
                            self.call_error(f"不明な変数名{node.ident}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", span.line, span.col, span.len)])
                            return
                    self.call_error(f"不明な変数名{node.ident}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", node.line, node.col, node.len)])
                    return
                self.call_error(f"不明な変数名{node.ident}, 現在の環境には存在しません。", node,
                    help=[
                        KinakoHelp(f"今の環境, Variable:{"\n".join([i.__repr__() for i in self.scope.get_variable_db()])}"),
                    ])
            case _:
                nodes = node.get_child()
                for i in nodes:
                    if isinstance(i, _expr.Expr):
                        self._visit_expr(i)
                return