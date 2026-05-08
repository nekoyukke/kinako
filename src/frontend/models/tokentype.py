from enum import Enum

class TokenType(Enum):
    # 演算子
    DOT = r'\.'
    DOUBLE_DOT = r'\.\.'
    ARROW = r'->'

    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='
    
    PLUS = r'\+'
    MINUS = r'-'
    MULT = r'\*'
    DIV = r'/'
    ADDR = r'&'
    MOD = r'%'
    LOGIC_OR = r'\|\|'
    LOGIC_AND = r'&&'

    ASSIGN = r'='
    AS = r'as\b'
    MOVE = r'move'
    CAST = r'cast\b'

    # リテラル
    NONE = r'none\b'
    NULL = r'null\b'
    
    # バン
    ANCHOR_BANG = r'@'

    # 構文
    IF = r'if\b'
    ELSE = r'else\b'
    FOR = r'for\b'
    WHILE = r'while\b'
    IMPORT = r'import\b'
    FN = r'fn\b'
    RETURN = r'return\b'

    # 組み込み占有権関連
    LET = r'let\b'
    CONST = r'const\b'
    MUT = r'mut\b'

    # 後付け系
    ANCHOR = r'anchor\b'
    HOLD = r'hold\b'
    GRAB = r'grab\b'

    # キーワード
    LABRACKET = r'<'
    RABRACKET = r'>'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    SEMI = r';'
    COMMA = r','

    # 型
    tNUMBER = r'Number\b'
    tDECIMAL = r'Decimal\b'
    tSTRING = r'String\b'
    tANY = r'Any\b'
    tLIST = r'List\b'
    tARRAY = r'Array\b'
    tAUTO = r'auto\b'
    tMAP = r'Map\b'
    tPTR = r'Ptr\b'
    tBOOL = r'Bool\b'
    tTUPLE = r'Tuple\b'
    tFUNCTION = r'Function\b'
    tCLASS = r'Class\b'

    # MEM
    tINT8 = r'int8\b'
    tUINT8 = r'uint8\b'
    tINT16 = r'int16\b'
    tUINT16 = r'uint16\b'
    tINT32 = r'int32\b'
    tUINT32 = r'uint32\b'
    tINT64 = r'int64\b'
    tUINT64 = r'uint64\b'
    tINT128 = r'int128\b'
    tUINT128 = r'uint128\b'

    tFLOAT32 = r'float32\b'
    tFLOAT64 = r'float64\b'
    tFLOAT = r'float\b'
    tDOUBLE = r'double\b'
    tINT = r'int\b'
    tLONG = r'long\b'
    tSHORT = r'short\b'
    tCHAR = r'char\b'

    # 可変
    DECIMAL = r'\d+\.\d+'
    SKIP = r'\s+'
    STRING = r'"(\\.|[^"\\])*"'
    NUMBER  = r'\d+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    COMMENT = r'//.+'

    # 特殊
    EOF = ""

GENERIC = {"tLIST", "tARRAY", "tMAP", "tPTR", "tTUPLE", "tFUNCTION"}

NOT_GEMERIC = tuple(
    t for t in TokenType
    if t.name.startswith("t") and t.name not in GENERIC
)
