from enum import Enum

class TokenType(Enum):
    # 演算子
    COMMENT = r'//[^\n]*'
    
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
    # リテラル
    NONE = r'none\b'
    NULL = r'null\b'
    
    # バン
    UNION = r'\|'

    # 構文
    IF = r'if\b'
    ELSE = r'else\b'
    ELIF = r'elif\b'
    FOR = r'for\b'
    WHILE = r'while\b'
    IMPORT = r'import\b'
    FN = r'fn\b'
    RETURN = r'return\b'
    IN = r'in\b'
    LET = r'let\b'

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
    COLON = r':'

    # 可変
    DECIMAL = r'\d+\.\d+'
    SKIP = r'\s+'
    STRING = r'"(\\.|[^"\\])*"'
    NUMBER  = r'\d+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'


    # 特殊
    EOF = ""
