import difflib
from dataclasses import dataclass, field

import src.core.context.context as _ctx
from src.core.symbol.symbol_def import Symbol
from src.core.source.source_span import SourceSpan

import src.frontend.parser.models.stmt as _stmt
import src.frontend.parser.models.expr as _expr
import src.frontend.parser.models.base as _base
from src.utils.error.resolver import KinakoResolverError
from src.utils.error.base import KinakoHelp, KinakoRelatedInfo, KinakoBaseError


@dataclass
class Scope:
    parent: "Scope | None" = None
    variables: dict[str, Symbol] = field(default_factory=dict[str, Symbol])

    def check(self, name:str):
        return name in self.variables

    def define(self, var: Symbol):
        self.variables[var.name] = var

    def lookup(self, name: str) -> Symbol | None:
        if self.check(name):
            return self.variables[name]
        if self.parent:
            return self.parent.lookup(name)
        return
    
    def get_variable(self) -> list[str]:
        if self.parent:
            return self.parent.get_variable() + list(self.variables)
        return list(self.variables)
    
    def get_variable_db(self, sc:int=0) -> list[str]:
        if self.parent:
            return self.parent.get_variable_db(sc+1) + [f"{sc}:{i}" for _,i in self.variables.items()]
        return [f"{sc}:{i}" for _,i in self.variables.items()]

class Resolver:
    def __init__(self, program:_stmt.ProgramStmt, source: str, context:_ctx.Context) -> None:
        self.program = program
        self.context = context
        self.source = source
        self.error:list[KinakoBaseError] = []
        self.scope = Scope()
    
    def resolve(self):
        # トップレベルに限らず、すべての定義を参照。
        return self._visit_program()

    def call_error(self, message:str, node:_base.ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoResolverError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
    
    def push_scope(self):
        self.scope = Scope(parent=self.scope)

    def pop_scope(self, node:_base.ASTNode):
        if self.scope.parent is None:
            self.call_error(f"kinakoコンパイラーエラー不明なスコープ取引、デバッグ情報:{self.scope.variables}", node)
            raise
        self.scope = self.scope.parent
    
    def get_names(self, name:str, cc:int=1) -> list[str]:
        names:list[str] = []
        names += list(self.context.functions.keys())
        names += list(self.context.policies.keys())
        names += list(self.context.policy_aliases.keys())
        names += list(self.context.rights.keys())
        names += list(self.context.right_aliases.keys())
        names += list(self.context.types.keys())
        names += list(self.context.type_aliases.keys())
        names += self.scope.get_variable()
        return difflib.get_close_matches(name, names, cc)

    def check_contract(self, contract:_base.Contract, node:_base.ASTNode):
        _type = None if contract.type is None else contract.type
        if _type:
            if not _type.name in self.context.policies | self.context.policy_aliases:
                name = self.get_names(_type.name.name)[0]
                other = self.context.functions[name].span
                if name:
                    self.call_error(f"不明なポリシー名。{_type.name}", node, related=[KinakoRelatedInfo(f"{name}ではありませんか？", other.line, other.col, other.len)])
                else:
                    self.call_error(f"不明なポリシー名。{_type.name}", node,)
        _policy = None if contract.policy is None else contract.policy
        if _policy:
            if not _policy.name in self.context.policies | self.context.policy_aliases:
                name = self.get_names(_policy.name.name)[0]
                other = self.context.functions[name].span
                if name:
                    self.call_error(f"不明なポリシー名。{_policy.name}", node, related=[KinakoRelatedInfo(f"{name}ではありませんか？", other.line, other.col, other.len)])
                else:
                    self.call_error(f"不明なポリシー名。{_policy.name}", node,)
        _right = None if contract.right is None else contract.right
        if _right:
            if not _right.name in self.context.rights | self.context.right_aliases:
                name = self.get_names(_right.name.name)[0]
                other = self.context.functions[name].span
                if name:
                    self.call_error(f"不明な権利名。{_right.name}", node, related=[KinakoRelatedInfo(f"{name}ではありませんか？", other.line, other.col, other.len)])
                else:
                    self.call_error(f"不明な権利名。{_right.name}", node,)
        
        return (_type, _right, _policy)

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

                name = node.name.ident.name
                if self.scope.check(name):
                    other = self.scope.lookup(name)
                    if other is not None:
                        span = other.span
                        self.call_error("宣言がかぶっています。", node, related=[KinakoRelatedInfo("被っている宣言元:", span.line, span.col, span.len)])
                        return
                    elif node.name.ident.name in self.context.functions:
                        span = self.context.functions[node.name.ident.name].span
                        self.call_error("宣言がかぶっています。", node, related=[KinakoRelatedInfo("被っている宣言元:", span.line, span.col, span.len)])
                        return
                    else:
                        self.call_error("宣言がかぶっています。", node)
                        return
                _type, _right, _policy = self.check_contract(node.contract, node)
                var = Symbol(
                    name,
                    SourceSpan(node.line, node.col, node.len),
                )
                self.scope.define(
                    var
                )
                self.context.resolved[self._get_node_id(node.name)] = var
                return
            case _stmt.FunctionDeclStmt():
                self.push_scope()

                for i in node.params:
                    name = i.name
                    self.scope.check(name)
                    _type, _right, _policy = self.check_contract(i.contract, node)
                    var = Symbol(
                        name,
                        SourceSpan(node.line, node.col, node.len),
                    )
                    self.scope.define(
                        var
                    )
                    self.context.resolved[self._get_node_id(node.name)] = var
                
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
                            self.call_error(f"不明な変数名{node.ident.name}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", other.span.line, other.span.col, other.span.len)])
                        elif node.ident.name in self.context.functions:
                            span = self.context.functions[node.ident.name].span
                            self.call_error(f"不明な変数名{node.ident.name}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", span.line, span.col, span.len)])
                            return
                    self.call_error(f"不明な変数名{node.ident.name}", node, related=[KinakoRelatedInfo(f"もしかしたら{name[0]}ではありませんか？", node.line, node.col, node.len)])
                    return
                self.call_error(f"不明な変数名{node.ident.name}, 現在の環境には存在しません。", node,
                    help=[
                        KinakoHelp(f"今の環境, Variable:{"\n".join([i.__repr__() for i in self.scope.get_variable_db()])}"),
                        KinakoHelp(f"context情報:{"\n".join([repr(k) + ":" + repr(v) for k, v in self.context.resolved.items()])}"),
                    ])
            case _:
                nodes = node.get_child()
                for i in nodes:
                    if isinstance(i, _expr.Expr):
                        self._visit_expr(i)
                return