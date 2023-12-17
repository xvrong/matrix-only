from ply.lex import LexToken
import ply.yacc as yacc
import ast1
from lexer import *
from enums import *
from error import *


def p_comp_unit(p):
    '''comp_unit : declaration_nest'''
    p[0] = ast1.CompUnit(p.lineno(1))
    for decl in p[1]:
        p[0].add_declaration(decl)


def p_declaration_nest(p):
    '''declaration_nest : declaration declaration_nest
                        | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_declaration(p):
    '''declaration : block_decl
                   | template_decl
                   | func_def'''
    p[0] = p[1]


def p_block_decl(p):
    '''block_decl : typedef_decl SEMICOLON
                  | struct_decl SEMICOLON
                  | var_decl SEMICOLON
                  | const_decl SEMICOLON
                  | func_decl SEMICOLON'''
    p[0] = p[1]


def p_typedef_decl(p):
    '''typedef_decl : TYPEDEF ID ASSIGN type_spec'''
    context["typedef"].append(p[2])
    p[0] = ast1.TypeDefDecl(p.lineno(1), p[2], p[4])


def p_var_decl(p):
    '''var_decl : VAR init_decl init_decl_nest'''
    p[0] = ast1.VarDecl(p.lineno(1), [p[2]] + p[3], False)


def p_const_decl(p):
    '''const_decl : CONST init_decl init_decl_nest'''
    p[0] = ast1.VarDecl(p.lineno(1), [p[2]] + p[3], True)


def p_init_decl_nest(p):
    '''init_decl_nest : COMMA init_decl init_decl_nest
                      | empty'''
    if p[1]:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_init_decl(p):
    '''init_decl : type_spec_opt ID assign_opt'''
    p[0] = ast1.InitDecl(p.lineno(1), p[1], p[2], p[3])


def p_assign_opt(p):
    '''assign_opt : ASSIGN expression
                  | empty'''
    if p[1]:
        p[0] = p[2]
    else:
        p[0] = None


def p_type_spec_opt(p):
    '''type_spec_opt : type_spec COLON
                     | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = None


def p_func_decl(p):
    '''func_decl : FUNC ID func_type'''
    p[0] = ast1.FuncDecl(p.lineno(1), p[2], p[3])


def p_template_decl(p):
    '''template_decl : TEMPLATE generic_type_list declaration'''
    context["generic_type"].clear()
    p[0] = ast1.TemplateDecl(p.lineno(1), p[2], p[3])


def p_generic_type_list(p):
    '''generic_type_list : LSS generic_type_decl generic_type_nest GRE'''
    p[0] = [p[2]] + p[3]


def p_generic_type_nest(p):
    '''generic_type_nest : COMMA generic_type_decl generic_type_nest
                         | empty'''
    if p[1]:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_generic_type_decl(p):
    '''generic_type_decl : ID'''
    context["generic_type"].append(p[1])
    p[0] = ast1.GenericTypeDecl(p.lineno(1), p[1])


def p_func_def(p):
    '''func_def : func_decl block_stmt'''
    p[0] = ast1.FuncDef(p.lineno(1), p[1], p[2])


def p_main_func_def(p):
    '''main_func_def : FUNC MAIN LPARENT RPARENT block_stmt'''
    p[0] = ast1.MainFuncDef(p.lineno(1), p[5])


def p_type_spec(p):
    '''type_spec : b_type
                 | struct_type
                 | generic_type
                 | defined_type
                 | array_type
                 | refer_type
                 | func_type'''
    p[0] = p[1]


def p_b_type(p):
    '''b_type : VOID
              | BOOL
              | INT
              | F16
              | F32
              | F64'''
    p[0] = ast1.BType(p.lineno(1), BasicType[p.slice[1].type])


def p_defined_type(p):
    '''defined_type : TYPEDEFID'''
    p[0] = ast1.DefinedType(p.lineno(1), p[1])


def p_generic_type(p):
    '''generic_type : GENERICID'''
    p[0] = ast1.GenericType(p.lineno(1), p[1])


def p_array_type(p):
    '''array_type : type_spec LBRACK int_literal_opt RBRACK'''
    p[0] = ast1.ArrayType(p.lineno(1), p[1], p[3])


def p_int_literal_opt(p):
    '''int_literal_opt : INT
                       | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = None


def p_refer_type(p):
    '''refer_type : AND type_spec'''
    p[0] = ast1.ReferType(p.lineno(1), p[2])


def p_struct_type(p):
    '''struct_type : STRUCTID generic_spec_list_opt'''
    p[0] = ast1.StructType(p.lineno(1), p[1], p[2])


def p_generic_spec_list_opt(p):
    '''generic_spec_list_opt : LSS type_spec generic_type_spec_nest GRE
                             | empty'''
    if p[1]:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_generic_type_spec_nest(p):
    '''generic_type_spec_nest : COMMA type_spec generic_type_spec_nest
                              | empty'''
    if p[1]:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_func_type(p):
    '''func_type : LPARENT func_param_list_opt RPARENT ret_type_opt'''
    p[0] = ast1.FuncType(p.lineno(1), p[2], p[4])


def p_ret_type_opt(p):
    '''ret_type_opt : ASSIGN type_spec
                    | empty'''
    if p[1]:
        p[0] = p[2]
    else:
        p[0] = None


def p_func_param_list_opt(p):
    '''func_param_list_opt : func_param func_param_nest
                           | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_func_param_nest(p):
    '''func_param_nest : COMMA func_param func_param_nest
                       | empty'''
    if p[1]:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_func_param(p):
    '''func_param : type_spec_opt ID'''
    p[0] = ast1.FuncParam(p.lineno(1), p[1], p[2])


############################################################## 结构体
def p_struct_decl(p):
    '''struct_decl : STRUCT ID new_struct LBRACE struct_member_nest RBRACE'''
    p[0] = ast1.StructDecl(p.lineno(1), p[2], p[5])


def p_new_struct(p):
    '''new_struct :'''
    context["struct"].append(p[-1])


def p_struct_member_nest(p):
    '''struct_member_nest : struct_member struct_member_nest
                          | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_struct_member(p):
    '''struct_member : member_var_decl
                     | member_func_def
                     | cons_func_def'''
    p[0] = p[1]


def p_member_var_decl(p):
    '''member_var_decl : type_spec COLON ID SEMICOLON'''
    p[0] = ast1.MemberVarDecl(p.lineno(1), p[3], p[1])


def p_member_func_def(p):
    '''member_func_def : func_def'''
    p[0] = ast1.MemberFuncDef(p.lineno(1), p[1])


def p_cons_func_def(p):
    '''cons_func_def : FUNC struct_type func_type block_stmt'''
    p[0] = ast1.ConsFuncDef(p.lineno(1), p[2], p[3], p[4])


def p_stmt(p):
    '''stmt : block_stmt
            | decl_stmt
            | exp_stmt
            | if_stmt
            | while_stmt
            | for_stmt
            | break_stmt
            | continue_stmt
            | return_stmt'''
    p[0] = p[1]


def p_block_stmt(p):
    '''block_stmt : LBRACE stmt_nest RBRACE'''
    p[0] = ast1.BlockStmt(p.lineno(1), p[2])


def p_stmt_nest(p):
    '''stmt_nest : stmt stmt_nest
                 | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_decl_stmt(p):
    '''decl_stmt : var_decl SEMICOLON
                 | const_decl SEMICOLON'''
    p[0] = ast1.DeclStmt(p.lineno(1), p[1])


def p_exp_stmt(p):
    '''exp_stmt : expression_opt SEMICOLON'''
    p[0] = ast1.ExpStmt(p.lineno(1), p[1])


def p_expression_opt(p):
    '''expression_opt : expression
                      | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = None


def p_if_stmt(p):
    '''if_stmt : IF LPARENT expression RPARENT stmt if_stmt_else_opt'''
    p[0] = ast1.IfStmt(p.lineno(1), p[3], p[5], p[6])


def p_if_stmt_else_opt(p):
    '''if_stmt_else_opt : ELSE stmt
                        | empty'''
    if p[1]:
        p[0] = p[2]
    else:
        p[0] = None


def p_while_stmt(p):
    '''while_stmt : WHILE LPARENT expression RPARENT stmt'''
    p[0] = ast1.WhileStmt(p.lineno(1), p[3], p[5])


def p_for_stmt(p):
    '''for_stmt : FOR LPARENT for_init_stmt expression_opt SEMICOLON expression_opt RPARENT stmt'''
    p[0] = ast1.ForStmt(p.lineno(1), p[3], p[4], p[6], p[8])


def p_for_init_stmt(p):
    '''for_init_stmt : exp_stmt
                     | decl_stmt'''
    p[0] = p[1]


def p_break_stmt(p):
    '''break_stmt : BREAK SEMICOLON'''
    p[0] = ast1.BreakStmt(p.lineno(1))


def p_continue_stmt(p):
    '''continue_stmt : CONTINUE SEMICOLON'''
    p[0] = ast1.ContinueStmt(p.lineno(1))


def p_return_stmt(p):
    '''return_stmt : RETURN expression_opt SEMICOLON'''
    p[0] = ast1.ReturnStmt(p.lineno(1), p[2])


def p_expression(p):
    '''expression : assign_exp
                  | binary_exp
                  | unary_exp
                  | postfix_exp'''
    p[0] = p[1]


def p_assign_exp(p):
    '''assign_exp : expression ASSIGN expression'''
    p[0] = ast1.AssignExp(p.lineno(1), p[1], p[3])


# + - * / & == > >= < <= && || ! << >> != % | ^
def p_binary_exp(p):
    '''binary_exp : expression PLUS expression
                   | expression MINUS expression
                   | expression MUL expression
                   | expression DIV expression
                   | expression AND expression
                   | expression OR expression
                   | expression XOR expression
                   | expression MOD expression
                   | expression LSHIFT expression
                   | expression RSHIFT expression
                   | expression LOGICOR expression
                   | expression LOGICAND expression
                   | expression NEQ expression
                   | expression EQ expression
                   | expression LEQ expression
                   | expression LSS expression
                   | expression GEQ expression
                   | expression GRE expression'''
    p[0] = ast1.BinaryExp(p.lineno(1), p[1], p[3], BinaryOp[p.slice[2].type])


def p_unary_exp(p):
    '''unary_exp : unary_op expression '''
    p[0] = ast1.UnaryExp(p.lineno(1), p[2], p[1])


def p_unary_op(p):
    '''unary_op : NOT
                | LOGICNOT
                | PLUS %prec UPLUS
                | MINUS %prec UMINUS'''
    if p[1]:
        p[0] = UnaryOp[p.slice[1].type]


def p_postfix_exp(p):
    '''postfix_exp : primary_exp
                   | array_index_exp
                   | member_exp
                   | refer_exp
                   | cast_exp
                   | call_func_exp
                   | io_exp
                   | lambda_exp'''
    p[0] = p[1]


def p_primary_exp(p):
    '''primary_exp : INTCON
                   | FLOATCON
                   | ID
                   | LPARENT expression RPARENT'''
    if p[1] == '(':
        p[0] = ast1.ExpPri(p.lineno(1), p.slice[2])
    elif p.slice[1].type == 'ID':
        p[0] = ast1.IdentPri(p.lineno(1), p.slice[1])
    elif p.slice[1].type == 'FLOATCON':
        # print(p[1])
        p[0] = ast1.LiteralPri(p.lineno(1), p.slice[1])
    else:
        p[0] = ast1.LiteralPri(p.lineno(1), p.slice[1])


def p_array_index_exp(p):
    '''array_index_exp : postfix_exp LBRACK expression RBRACK'''
    p[0] = ast1.ArrayIndexExp(p.lineno(2), p[1], p[3])


def p_member_exp(p):
    '''member_exp : postfix_exp DOT ID'''
    p[0] = ast1.MemberExp(p.lineno(1), p[1], p[3])


def p_refer_exp(p):
    '''refer_exp : AND LPARENT expression RPARENT'''
    p[0] = ast1.ReferExp(p.lineno(2), p[3])


def p_cast_exp(p):
    '''cast_exp : LPARENT type_spec RPARENT expression'''
    p[0] = ast1.CastExp(p.lineno(1), p[2], p[4])


def p_func_call_exp(p):
    '''call_func_exp : postfix_exp generic_spec_list_opt LPARENT func_real_param_list_opt RPARENT'''
    p[0] = ast1.FuncCallExp(p.lineno(4), p[1], p[2], p[4])


def p_func_real_param_list_opt(p):
    '''func_real_param_list_opt : expression func_real_param_nest
                                | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_func_real_param_nest(p):
    '''func_real_param_nest : expression func_real_param_nest
                            | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_lambda_exp(p):
    '''lambda_exp : FUNC func_type block_stmt'''
    p[0] = ast1.LambdaExp(p.lineno(1), p[2], p[3])


def p_io_expr(p):
    '''io_exp : SCAN LSS type_spec GRE LPARENT ID RPARENT
               | PRINT LSS type_spec GRE LPARENT expression RPARENT'''
    if IOType[p.slice[1].type] == 0:
        p[0] = ast1.IOExp(p.lineno(1), p[1], p[3], p[6], None)
    else:
        p[0] = ast1.IOExp(p.lineno(1), p[1], p[3], "", p[6])


def p_empty(p):
    'empty :'
    p[0] = None


precedence = (
    ('left', 'LOGICOR'),
    ('left', 'LOGICAND'),
    ('left', 'OR'),
    ('left', 'XOR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'LSS', 'LEQ', 'GRE', 'GEQ'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV', 'MOD', ),
    ('right', 'UMINUS', 'UPLUS', 'LOGICNOT', 'NOT'),            # Unary minus operator
)


# Error rule for syntax errors
def p_error(p: LexToken):
    # print(f"Syntax error at token {p.lineno} {p.type}")
    # yacc.errok()
    raise ParseError(f'Syntax error at line {p.lineno}: {p.value}')


# Build the parser
def create_parser(debug=None):
    return yacc.yacc(start='comp_unit', debug=debug)
