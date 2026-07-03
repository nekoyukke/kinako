from src.core.context.context import *
from src.core.right.right_def import *
from src.core.source.source_span import *
from src.core.identifier.identifier import *

zero = SourceSpan(0,0,0)

def inject_builtin_types(ctx:Context):
    ctx.types["int"] = TypeDef("int", zero)
    ctx.types["string"] = TypeDef("string", zero)
    ctx.types["bool"] = TypeDef("bool", zero)

def inject_builtin_rights(ctx:Context):
    ctx.rights["Read"] = RightDef(Access.READ, Identity.NONE, zero)
    ctx.rights["Write"] = RightDef(Access.WRITE, Identity.NONE, zero)
    ctx.rights["Unique"] = RightDef(Access.NONE, Identity.UNIQUE, zero)
    ctx.rights["Shared"] = RightDef(Access.NONE, Identity.SHARED, zero)

def inject_builtin_policies(ctx:Context):
    ctx.policies["Arc"] = PolicyDef("Arc", zero)
    ctx.policies["Mutex"] = PolicyDef("Mutex", zero)

def inject_builtin_alias(ctx:Context):
    ctx.right_aliases["Onwer"] = RightAliasDef("Onwer", [Identifier(Variable("Read"), []), Identifier(Variable("Unique"), [])], zero)

def inject_builtins(ctx: Context) -> Context:
    inject_builtin_types(ctx)
    inject_builtin_rights(ctx)
    inject_builtin_policies(ctx)
    return ctx