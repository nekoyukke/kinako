
from src.core.symbol.symbol import Symbol
from src.core.type.type import Type
from src.core.place.place import Place


class CompilationContext:
    symbol_table: dict[str, Symbol]
    scope_table: dict[int, int]

    type_table: dict[int, Type]

    ownership_table: dict[int, Ownership]

    errors: list[Error]