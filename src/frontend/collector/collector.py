
from src.core.context.context import CompilationContext

import src.frontend.parser.models.expr as expr
import src.frontend.parser.models.stmt as stmt
import src.frontend.parser.models.literal as literal

from src.utils.error.collect import KinakoCollectError

class Collector():
    def __init__(self, program: stmt.Program, source:str, context:CompilationContext) -> None:
        self.program = program
        self.source = source
        self.context = context

    def collect(self):
        for block in self.program.blocks:
            self._visit_try_stmt(block)
        return
    
    def _visit_try_stmt(self, stmt:stmt.Stmt):
        try:
            self._visit_stmt(stmt)
        except KinakoCollectError as e:
            