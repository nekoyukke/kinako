import difflib

import src.frontend.parser.models.stmt as _stmt
import src.frontend.parser.models.base as _base

from src.utils.error.collect import KinakoCollectError
from src.utils.error.base import KinakoHelp, KinakoBaseError, KinakoRelatedInfo

import src.core.context.context as _ctx
from src.core.function.function_def import FunctionDef, ParameterDef
from src.core.source.source_span import SourceSpan

class Collector:
    def __init__(self, program:_stmt.ProgramStmt, source:str, context: _ctx.Context) -> None:
        self.program = program
        self.source = source
        self.context = context
        self.error:list[KinakoBaseError] = []

    def call_error(self, message:str, node:_base.ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoCollectError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
        raise err

    def collect(self):
        # トップレベルにおいての順番を問わないもの
        for block in self.program.instr:
            self._visit_try_stmt(block)
        self.check()
        return
    
    def _visit_try_stmt(self, stmt:_stmt.Stmt):
        try:
            self._visit_stmt(stmt)
            return
        except KinakoCollectError:
            return
    
    def _visit_stmt(self, node:_stmt.Stmt):
        match (node):
            case _stmt.FunctionDeclStmt():
                # 私にすらわかる
                if (node.name.ident.name in self.context.functions):
                    other = self.context.functions[node.name.ident.name].span
                    self.call_error(f"関数名'{node.name.ident.name}'がかぶっています", node, related=[KinakoRelatedInfo("かぶっている宣言元:", other.line, other.col, other.len)])
                    raise

                params: list[ParameterDef] = []
                for param in node.params:
                    # Noneチェックとセット
                    _type = None if param.contract.type is None else param.contract.type
                    _policy = None if param.contract.policy is None else param.contract.policy
                    _right = None if param.contract.right is None else param.contract.right

                    params += [ParameterDef(
                        param.name,
                        SourceSpan(node.line, node.col, node.len),
                        _type,
                        _policy,
                        _right,
                    )]

                # Noneチェックとセット
                _type = None if node.result.type is None else node.result.type
                _policy = None if node.result.policy is None else node.result.policy
                _right = None if node.result.right is None else node.result.right

                self.context.functions[node.name.ident.name] = FunctionDef(
                    node.name.ident.name,
                    SourceSpan(node.line, node.col, node.len),
                    params,
                    _type,
                    _policy,
                    _right,
                )
            case _:
                return

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
    
    def check(self):
        for block in self.program.instr:
            self._check_try_stmt(block)

    def get_names(self, name:str, cc:int=1) -> list[str]:
        names:list[str] = []
        names += list(self.context.functions.keys())
        names += list(self.context.policies.keys())
        names += list(self.context.policy_aliases.keys())
        names += list(self.context.rights.keys())
        names += list(self.context.right_aliases.keys())
        names += list(self.context.types.keys())
        names += list(self.context.type_aliases.keys())
        return difflib.get_close_matches(name, names, cc)
    
    def _check_try_stmt(self, stmt:_stmt.Stmt):
        try:
            self._check_stmt(stmt)
            return
        except KinakoCollectError:
            return
    
    def _check_stmt(self, node:_stmt.Stmt):
        match (node):
            case _stmt.FunctionDeclStmt():
                # 私にすらわかる
                self.check_contract(node.result, node)
                for i in node.params:
                    self.check_contract(i.contract, node)
            case _:
                return