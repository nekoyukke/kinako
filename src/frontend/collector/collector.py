from contextlib import contextmanager

from src.core.id_base.scope_id import ScopeId
from src.core.id_base.symbol_id import SymbolId
from src.core.id_base.possession_id import PossessionId

from src.core.context.context import CompilationContext
from src.core.symbol.symbol import Symbol
from src.core.possession.possession import Possession, PossessionFlag


import src.frontend.parser.models.stmt as stmt
from src.core.node.ast_base import ASTNode
from src.core.scope.scope import Scope

from src.utils.error.collect import KinakoCollectError
from src.utils.error.base import KinakoBaseError, KinakoHelp, KinakoRelatedInfo

class Collector():
    def __init__(self, program: stmt.Program, source:str, context:CompilationContext) -> None:
        self.program = program
        self.source = source
        self.context = context
        self.num_of_scope = 0
        self.num_of_symbol = 0
        self.num_of_possession = 0
        self.error: list[KinakoBaseError] = []
        self.scope = self.make_scope()

    def make_scope(self) -> Scope:
        id = self.idscope()
        this = Scope(id, {}, None)
        self.context.symbol.scope_table[id] = this
        return this
    
    def new_scope(self) -> Scope:
        id = self.idscope()
        this = Scope(id, {}, self.scope.me)
        self.context.symbol.scope_table[id] = this
        return this
    
    def del_scope(self) -> Scope:
        if self.scope.parent is None: # スロー
            err = KinakoCollectError(
                f"コンパイラエラー！静的チェックエラー。スコープが不明です。\nデバッグ情報スコープ:{self.scope}",
                0, 0, self.source, 0,
                [KinakoRelatedInfo("コンパイラーエラー。実行不可能です",0,0,0)],
                [KinakoHelp("コンパイラーのバグです。修正されるべき。")])
            self.error += [err]
            raise err
        return self.context.symbol.scope_table[self.scope.parent]
    
    @contextmanager
    def with_scope(self):
        self.scope = self.new_scope()
        yield
        self.scope = self.del_scope()
    
    def call_error(self, message:str, node:ASTNode, related:list[KinakoRelatedInfo]=[], help:list[KinakoHelp]=[]):
        err = KinakoCollectError(message, node.line, node.col, self.source, node.len, related, help)
        self.error.append(err)
        raise err

    def idscope(self) -> ScopeId:
        res = ScopeId(self.num_of_scope)
        self.num_of_scope += 1
        return res

    def idsym(self) -> SymbolId:
        res = SymbolId(self.num_of_symbol)
        self.num_of_symbol += 1
        return res

    def idpos(self) -> PossessionId:
        res = PossessionId(self.num_of_possession)
        self.num_of_possession += 1
        return res
    
    def collect(self):
        for block in self.program.blocks:
            self._visit_try_stmt(block)
        return
    
    def _visit_try_stmt(self, node:stmt.Stmt):
        try:
            self._visit_stmt(node)
            return
        except KinakoCollectError:
            return
    

    def get_fq(self, name:str):
        return f"{self.get_scope_fq(self.scope)}.{name}"
        
    def get_scope_fq(self, scope:Scope):
        if scope.parent is None:
            return f"{scope.me}"
        return f"{self.get_scope_fq(self.context.symbol.scope_table[scope.parent])}.{scope.me}"

    def get_scopeid(self):
        return ScopeId(self.num_of_scope - 1)

    def _visit_fn_args(self, node:stmt.FunctionDefineNode):
        for i in range(len(node.arg_Possession)-1):
            if node.args[i].name in self.scope.symbols:
                s_id = self.scope.symbols[node.args[i].name]
                n = self.context.symbol.decl_node[s_id]
                self.call_error(
                    f"名称がかぶっています！", node.args[i],
                    related=[KinakoRelatedInfo(f"すでに宣言された場所。", n.line, n.col, n.len)],
                    help=[KinakoHelp(f"'{node.args[i].name}'の名称を変更しますか？")]
                )
            id = node.args[i].id
            symid = self.idsym()
            posid = self.idpos()
            sym = Symbol(id=symid, fq_name=self.get_fq(node.args[i].name), name=node.args[i].name,
                         decl_node=id, possession_id=posid, scope_id=self.scope.me)
            self.context.symbol.symbol_table[symid] = sym
            self.context.symbol.possession_table[posid] = node.arg_Possession[i]
            self.context.symbol.decl_node[symid] = node.args[i]
            self.scope.symbols[node.args[i].name] = symid

    def set_scopeId(self, node:ASTNode):
        value = self.get_scopeid()
        node.scopeid = value
        for i in node.get_child():
            self.set_scopeId(i)
        return


    def _visit_stmt(self, node:stmt.Stmt):
        self.set_scopeId(node)
        match (node):
            case stmt.LetStmt():
                
                if node.name.name in self.scope.symbols:
                    s_id = self.scope.symbols[node.name.name]
                    n = self.context.symbol.decl_node[s_id]
                    self.call_error(
                        f"名称がかぶっています！", node,
                        related=[KinakoRelatedInfo(f"すでに宣言された場所。", n.line, n.col, n.len)],
                        help=[KinakoHelp(f"'{node.name.name}'の名称を変更しますか？")]
                    )
                symid = self.idsym()
                posid = self.idpos()
                sym = Symbol(id=symid, fq_name=self.get_fq(node.name.name), name=node.name.name,
                             decl_node=node.id, possession_id=posid, scope_id=self.scope.me)
                self.context.symbol.symbol_table[symid] = sym
                self.context.symbol.possession_table[posid] = node.kind
                self.context.symbol.decl_node[symid] = node
                self.scope.symbols[node.name.name] = symid
                return
            case stmt.FunctionDefineNode():
                
                if node.name.name in self.scope.symbols:
                    s_id = self.scope.symbols[node.name.name]
                    n = self.context.symbol.decl_node[s_id]
                    self.call_error(
                        f"名称がかぶっています！", node,
                        related=[KinakoRelatedInfo(f"すでに宣言された場所。", n.line, n.col, n.len)],
                        help=[KinakoHelp(f"'{node.name.name}'の名称を変更しますか？")]
                    )
                symid = self.idsym()
                posid = self.idpos()
                sym = Symbol(id=symid, fq_name=self.get_fq(node.name.name), name=node.name.name,
                             decl_node=node.id, possession_id=posid, scope_id=self.scope.me)
                self.context.symbol.symbol_table[symid] = sym
                self.context.symbol.possession_table[posid] = node.return_Possession
                self.context.symbol.decl_node[symid] = node
                self.scope.symbols[node.name.name] = symid

                if isinstance(node.body, stmt.BlockNode):
                    with self.with_scope():
                        self._visit_fn_args(node)
                        for n in node.body.stmts:
                            self._visit_try_stmt(n)
                    return

                with self.with_scope():
                    self._visit_fn_args(node)
                    self._visit_try_stmt(node.body)
                return
            
            case stmt.IfStmtNode():
                
                with self.with_scope():
                    self._visit_try_stmt(node.then_stmt)
                if node.else_stmt:
                    with self.with_scope():
                        self._visit_try_stmt(node.else_stmt)
                return
            case stmt.ForStmtNode():
                
                if isinstance(node.body, stmt.BlockNode):
                    with self.with_scope():
                        symid = self.idsym()
                        posid = self.idpos()
                        sym = Symbol(id=symid, fq_name=self.get_fq(node.var.name), name=node.var.name,
                                     decl_node=node.id, possession_id=posid, scope_id=self.scope.me)
                        self.context.symbol.symbol_table[symid] = sym
                        self.context.symbol.possession_table[posid] =\
                                Possession(
                                    flag=PossessionFlag.NONE,
                                    generic=None
                                )
                        self.context.symbol.decl_node[symid] = node
                        self.scope.symbols[node.var.name] = symid
                        for n in node.body.stmts:
                            self._visit_try_stmt(n)
                    return

                with self.with_scope():
                    self._visit_try_stmt(node.body)
                return
            case stmt.WhileStmtNode():
                
                with self.with_scope():
                    self._visit_try_stmt(node.body)
                return
            case stmt.BlockNode():
                
                with self.with_scope():
                    for n in node.stmts:
                        self._visit_try_stmt(n)
                return
            case stmt.HoldStmtNode() | stmt.GrabStmtNode() | stmt.AnchorStmtNode():
                
                with self.with_scope():
                    self._visit_try_stmt(node.then_stmt)
                if node.else_stmt:
                    with self.with_scope():
                        self._visit_try_stmt(node.else_stmt)
                return
            case _:
                
                return