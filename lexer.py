import ply.lex as lex
from ply.lex import TOKEN

context = {
    "struct": [],
    "typedef": [],
    "generic_type": [],
    # "generic_func": [],
    # "last_scope_is_struct": False,
}


def init_lexer_context():
    context["struct"].clear()  # struct
    context["typedef"].clear()  # typedef名
    context["generic_type"].clear()  # struct泛型名
    # context["generic_func"].clear()  # function泛型名
    # context["last_scope_is_struct"] = False


def query_name(name):
    # return None
    if name in context["struct"]:
        return 'STRUCTID'
    elif name in context["typedef"]:
        return 'TYPEDEFID'
    elif name in context["generic_type"]:
        return 'GENERICID'
    else:
        return None


# token名list
tokens = [
    'ID',               # 标识符
    'STRUCTID',         # Struct 标识符
    'TYPEDEFID',        # TypeDef 标识符
    'GENERICID',        # 泛型 标识符
    'INTCON',           # 10进制数字
    'FLOATCON',         # 32位浮点数
    # 'DOUBLECON',        # 64位浮点数
    'STRCON',           # 字符串
    'PLUS',             # +
    'MINUS',            # -
    'OR',               # |
    'XOR',              # ^
    'AND',              # &
    'NOT',              # ~
    'MUL',              # *
    'DIV',              # /
    'MOD',              # %
    'ASSIGNTYPE',       # ->
    'LSHIFT',           # <<
    'RSHIFT',           # >>
    'LOGICOR',          # ||
    'LOGICAND',         # &&
    'LOGICNOT',         # !
    'EQ',               # ==
    'NEQ',              # !=
    'LSS',              # <
    'LEQ',              # <=
    'GRE',              # >
    'GEQ',              # >=
    'ASSIGN',           # =
    'LPARENT',          # (
    'RPARENT',          # )
    'LBRACK',           # [
    'RBRACK',           # ]
    'LBRACE',           # {
    'RBRACE',           # }
    'COMMA',            # ,
    'COLON',            # :
    'DOT',              # .
    'SEMICOLON',        # ;
    'GENERICMARK',      # '
]

# 保留字
reserved = {
    'if'        : 'IF',
    'else'      : 'ELSE',
    'for'       : 'FOR',
    'while'     : 'WHILE',
    'continue'  : 'CONTINUE',
    'break'     : 'BREAK',
    'func'      : 'FUNC',
    'main'      : 'MAIN',
    'return'    : 'RETURN',
    'scan'      : 'SCAN',
    'print'     : 'PRINT',
    'ref'       : 'REF',
    'typedef'   : 'TYPEDEF',
    'var'       : 'VAR',
    'const'     : 'CONST',
    'auto'      : 'AUTO',
    'void'      : 'VOID',
    'bool'      : 'BOOL',
    'int'       : 'INT',
    'f16'       : 'F16',
    'f32'       : 'F32',
    'f64'       : 'F64',
    # 'float'     : 'FLOAT',
    # 'double'    : 'DOUBLE',
    'struct'    : 'STRUCT',
    'template'  : 'TEMPLATE',
}

tokens = tokens + list(reserved.values())


# 简单token
t_PLUS          = r'\+'
t_MINUS         = r'-'
t_OR            = r'\|'
t_XOR           = r'\^'
t_AND           = r'&'
t_NOT           = r'~'
t_MUL           = r'\*'
t_DIV           = r'/'
t_MOD           = r'%'
t_ASSIGNTYPE    = r'->'
t_LSHIFT        = r'<<'
t_RSHIFT        = r'>>'
t_LOGICOR       = r'\|\|'
t_LOGICAND      = r'&&'
t_LOGICNOT      = r'!'
t_EQ            = r'=='
t_NEQ           = r'!='
t_LEQ           = r'<='
t_GEQ           = r'>='
t_LSS           = r'<'
t_GRE           = r'>'
t_ASSIGN        = r'='
t_LPARENT       = r'\('
t_RPARENT       = r'\)'
t_LBRACK        = r'\['
t_RBRACK        = r'\]'
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_COMMA         = r','
t_COLON         = r':'
t_DOT           = r'\.'
t_SEMICOLON     = r';'
t_GENERICMARK   = r'\''



def t_FLOATCON(t):
    r'[-+]?(([0-9]*\.[0-9]+)|([0-9]+\.))'
    t.type = 'FLOATCON'
    # t.type = 'FLOATCON' if t.value[-1] == 'f' else 'DOUBLECON'
    # t.value = float(t.value[:-1] if t.value[-1] == 'f' else t.value)
    t.value = float(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value) or query_name(t.value) or 'ID'
    return t


def t_INTCON(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRINGCON(t):
    r'\"((\\.)|[^"\\\n])*\"'
    t.value = t.value[1:-1]
    return t


# 跟踪行号匹配规则
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 保存忽略字符，空格等
t_ignore = ' \t'

# 忽略注释
t_ignore_COMMENT = r'\#.*'


# 错误处理规则
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def create_lexer():
    return lex.lex()
