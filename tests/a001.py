from tests.util import *
print(*lexer(
"""
{
    a();
}
"""
), sep="\n")
# 2026-06-14-09-44: {がexpr_entryに入るので検証。EOFが二つあるので修正を