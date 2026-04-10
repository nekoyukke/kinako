from enum import Enum
import utils  # type: ignore


class TokenType(Enum):
    # 仮代入
    STR = "str"
    NUMBER = "NUMBER"
    DECIMAL = "DECIMAL"

    # リテラル類
    ID = "ID"
    VAL = "val"
    LET = "let"
    CONST = "const"
    BORROW = "borrow"
    MOVE = "move"
    MUT = "mut"
    IF = "if"
    ELSE = "else"
    ELIF = "elif"
    WHILE = "while"
    FOR = "for"
    FAMILY = "family"
    STATIC = "static"
    RETURN = "return"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "null"
    NONE = "none"
    FN = "fn"
    IMPORT = "import"
    IN = "in"
    ARGS = "...args"
    AS = "as"

    # アノテーション
    UNSAFE = "@unsafe"

    # 特別に用意するもの
    END = "@END@"
    DFFUNC = "@FUNC@" # 関数
    DFUNION = "@DFLIST@" # Nodeでリストを表すためにする（ゴミ仕様）
    DFACCESS = "@DFACCESS@" #アクセスとか
    DFMAP = "@MAP@" # マップ用
    DFLIST = "@LIST@" # リスト用
    DFARRAY = "@ARRAY@" # 配列
    DFTUPLE = "@TUPLE@" # タプル
    DFARGS = "@ARGS@" # 引数


    # 型
    tNUM = "Num"
    tDEC = "Dec"
    tSTR = "Str"
    tANY = "Any"
    tLIST = "List"
    tARRAY = "Array"
    tDYNAMIC = "Dynamic"
    tMAP = "Map"
    tPTR = "Ptr"
    tBOOL = "Bool"
    tTUPLE = "Tuple"
    tFUNCTION = "Function"
    tCLASS = "Class"

    #　自由型
    tANYNUMBER = "@number@"
    tANYFLOAT = "@float@"

    # 借用・所有権型
    tBORROW = "&borrow"

    # MEM
    tINT8 = "int8"
    tUINT8 = "uint8"
    tINT16 = "int16"
    tUINT16 = "uint16"
    tINT32 = "int32"
    tUINT32 = "uint32"
    tINT64 = "int64"
    tUINT64 = "uint64"
    tINT128 = "int128"
    tUINT128 = "uint128"

    tFLOAT32 = "float32"
    tFLOAT64 = "float64"
    tFLOAT = "float"
    tDOUBLE = "double"
    tINT = "int"
    tLONG = "long"
    tSHORT = "short"
    tCHAR = "char"

    # イコール
    ASSIGN = "="
    ADD_ASSIGN = "+="
    SUB_ASSIGN = "-="
    MUL_ASSIGN = "*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    NULLCOALESCING_ASSIGN = "?="
    NONECOALESCING_ASSIGN = "%%="
    
    # Union
    tUNION = "TYPE_UNION"
    
    # かっこ類
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    LABRACKET = "<"
    RABRACKET = ">"
    LPAREN = "("
    RPAREN = ")"
    
    # 演算子
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    EXP = "**"
    ADD = "&"
    DIV = "/"
    MOD = "%"
    LOGICAND = "&&"
    LOGICXOR = "^^"
    LOGICOR = "||"
    LOGICNOT = "!"
    BITNOT = "~"
    BITOR = "|"
    BITXOR = "^"
    BITAND = "&&&"
    SEMI = ";"
    COLON = ":"

    DOUBLEDOT = ".."

    INC = "++"
    DEC = "--"

    NULLCOALESCING = "??"
    NONECOALESCING = "%%%"
    ELVIS = "?:"
    NULLREJECT = "?!"
    NONEREJECT = "%%!"
    REJECT = "!!"
    COMMA = ","
    DOT = "."
    ARROW = "->"
    EQ = "=="
    NE = "!="
    EQSTRICT = "==="
    NESTRICT = "!=="
    LE = "<="
    GE = ">="
    CMP = "<=>"
    LSHIFT = "<<"
    RSHIFT = ">>"

    BACKQUOTE = "BACKQUOTE"

from dataclasses import dataclass

@dataclass
class Token(object):
    type: TokenType
    value: float | int | str
    line: int = 0
    column: int = 0
    String: str = ""
    
    @classmethod
    def zero(cls):
        return Token(TokenType.END, 0)

_t_int = (
    TokenType.tINT8,
    TokenType.tINT16,
    TokenType.tINT32,
    TokenType.tINT64,
    TokenType.tINT128,
    TokenType.tUINT8,
    TokenType.tUINT16,
    TokenType.tUINT32,
    TokenType.tUINT64,
    TokenType.tUINT128,
    TokenType.tCHAR,
    TokenType.tSHORT,
    TokenType.tINT,
    TokenType.tLONG,
)

_t_float = (
    TokenType.tFLOAT,
    TokenType.tFLOAT32,
    TokenType.tFLOAT64,
    TokenType.tDOUBLE,
)

_t_number = (
    TokenType.tANYNUMBER,
    TokenType.tNUM,
    *_t_int
)

_t_decimal = (
    TokenType.tDEC,
    *_t_float
)

_t_string = (
    TokenType.tSTR
)

_t_list = (
    TokenType.tLIST
)

_t_tuple = (
    TokenType.tTUPLE
)

_t_array = (
    TokenType.tARRAY
)

_t_dynamic = (
    TokenType.tDYNAMIC
)

_t_map = (
    TokenType.tMAP
)

_t_ptr = (
    TokenType.tPTR
)

_t_bool = (
    TokenType.tBOOL
)

_t_function = (
    TokenType.tFUNCTION
)

_t_class = (
    TokenType.tCLASS
)