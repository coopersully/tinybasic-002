# -----------------------------------------------------------------------------
# example.py
#
# Example of using PLY To parse the following simple grammar.
#
#   EXAMPLE VALID PROGRAM: 
#      let x=3*4;let y=4-1;3+x*y
#   EXAMPLE INVALID PROGRAM: (you can't have assignment statements at the end)
#      let x=3; let y=4; 3+x*y; let z=3; 
#
#   program : [assignment_list] expression
#
#   assignment_list : assignment ;
#              | assignment ; assignment_list
#
#   assignment : let NAME = expression
# 
#   expression : term PLUS term
#              | term MINUS term
#              | term
#
#   term       : factor TIMES factor
#              | factor DIVIDE factor
#              | factor
#
#   factor     : NUMBER
#              | NAME
#              | PLUS factor
#              | MINUS factor
#              | LPAREN expression RPAREN
#
# -----------------------------------------------------------------------------

from ply.lex import lex
from ply.yacc import yacc

# --- Tokenizer

# All tokens must be named in advance.
tokens = ('LET', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
          'NAME', 'NUMBER', 'EQUALS', 'SEMICOLON')

# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_SEMICOLON = r';'


# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # scan through all the reserved words and update the type
    if t.value == 'let' or t.value == 'LET':
        t.type = 'LET'
    return t


# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)


# Build the lexer object
lexer = lex()


# --- Parser

# Write functions for each grammar rule which is
# specified in the docstring.

def p_program_withassignments(p):
    '''
    program : assignment_list expression
    '''
    p[0] = ('assignments', p[1], p[2])


def p_program_noassignments(p):
    '''
    program : expression
    '''
    p[0] = p[1]


def p_assignment_listsingle(p):
    '''
    assignment_list : assignment SEMICOLON
    '''
    p[0] = (p[1])


def p_assignment_listmultiple(p):
    '''
    assignment_list : assignment SEMICOLON assignment_list
    '''
    p[0] = p[1] + p[3]


def p_assignment(p):
    '''
    assignment : LET NAME EQUALS expression
    '''
    p[0] = (p[2], p[
        4])  # this returns a tuple with variable name first, followed by the expression used to initialize the variable


def p_expression(p):
    '''
    expression : term PLUS term
               | term MINUS term
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : term PLUS term
    #   p[0]     : p[1] p[2] p[3]
    # 
    p[0] = ('binop', p[2], p[1], p[3])


def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]


def p_term(p):
    '''
    term : factor TIMES factor
         | factor DIVIDE factor
    '''
    p[0] = ('binop', p[2], p[1], p[3])


def p_term_factor(p):
    '''
    term : factor
    '''
    p[0] = p[1]


def p_factor_name(p):
    '''
    factor : NAME
    '''
    p[0] = ('name', p[1])


def p_factor_number(p):
    '''
    factor : NUMBER
    '''
    p[0] = ('number', p[1])


def p_factor_unary(p):
    '''
    factor : PLUS factor
           | MINUS factor
    '''
    p[0] = ('unary', p[1], p[2])


def p_factor_grouped(p):
    '''
    factor : LPAREN expression RPAREN
    '''
    p[0] = ('grouped', p[2])


def p_error(p):
    print(f'Syntax error at {p.value!r}')


# Build the parser
parser = yacc()

# Parse an expression
ast = parser.parse('let x=2;let y=4+x;(y+3)*x')
print(ast)


# OK, you've got the parse tree, now evaluate it!
def evaluateExpression(expr, symboltable):
    return 0


def populateSymbols(symbollist):
    symboltable = {}
    for i in range(len(symbollist)):
        if i % 2 == 0:
            symboltable[symbollist[i]] = evaluateExpression(symbollist[i + 1], symboltable)
    return symboltable


def evaluate(ast):
    if ast[0] == 'assignments':
        return evaluateExpression(ast[2], populateSymbols(ast[1]))
    else:
        return evaluateExpression(ast, {})