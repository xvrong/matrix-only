import ply.lex as lex
from ply.lex import TOKEN

context = {
    "struct" : [],
    "interface" : [],
    "type_alias" : [],
    "generic_top" : [],
    "generic_func" : [],
    "last_scope_is_top" : False,
}


def init_lexer_context():
    context["struct"].clear()  # strcut名
    context["interface"].clear()  # interface名
    context["type_alias"].clear()  # type_alias名
    context["generic_top"].clear()  # struct和interface的泛型名
    context["generic_func"].clear()  # function泛型名
    context["last_scope_is_top"] = False


def query_name(name):
    #return None
    if name in context["struct"]:
        return 'STRUCTID'
    elif name in context["interface"]:
        return 'INTERFACEID'
    elif name in context["type_alias"]:
        return 'TYPEALIASID'
    elif name in context["generic_top"] or name in context["generic_func"]:
        return 'GENERICID'
    else:
        return None


# token名list
tokens = [
    'ID',               # 标识符
    'STRUCTID',         # Struct 标识符
    'TYPEALIASID',      # TypeAlias 标识符
    'GENERICID',        # 泛型 标识符
    'INTCON',           # 10进制数字
    'FLOATCON',         # 32位浮点数
    'DOUBLECON',        # 64位浮点数
    'STRINGCON',        # 字符串
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
    'return'    : 'RETURN',
    'scan'      : 'SCAN',
    'print'     : 'PRINT',
    'ref'       : 'REF',
    'type'      : 'TYPE',
    'const'     : 'CONST',
    'auto'      : 'AUTO',
    'void'      : 'VOID',
    'bool'      : 'BOOL',
    'int'       : 'INT',
    'float'     : 'FLOAT',
    'double'    : 'DOUBLE',
    'struct'    : 'STRUCT'
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

# 复杂TOKEN
t_ID            = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_INTCON           = r'\d+'
t_FLOATCON         = r'[-+]?(([0-9]*\.[0-9]+)|([0-9]+\.))(f)?'
t_STRINGCON        = r'\"((\\.)|[^"\\\n])*\"'


@TOKEN(t_ID)
def t_ID(t):
    t.type = reserved.get(t.value) or query_name(t.value) or 'ID'
    return t


@TOKEN(t_INTCON)
def t_INTCON(t):
    t.value = int(t.value)
    return t


@TOKEN(t_FLOATCON)
def t_FLOATCON(t):
    t.type = 'FLOATCON' if t.value[-1] == 'f' else 'DOUBLECON'
    t.value = float(t.value[:-1] if t.value[-1] == 'f' else t.value)
    return t


@TOKEN(t_STRINGCON)
def t_STRINGCON(t):
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