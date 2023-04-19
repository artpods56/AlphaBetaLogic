class Formula():
    registry = set()
    
    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        Formula.registry.add(self)
    
    def to_prefix_notation(self):
        pass

class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        
    def to_prefix_notation(self):
        return self.letter



class Conjunction(Formula):
    def __init__(self, arguments: list):
        super().__init__()
        self.arguments = arguments


class Equivalence(Formula):
    def __init__(self, arguments: list):
        super().__init__()
        self.arguments = arguments

import re
from ply import lex, yacc

tokens = ['LPAREN','RPAREN','VARIABLE', 'CONJUNCTION', 'EQUIVALENCE']

t_ignore = ' \t\r\n\f\v'

literals = ['(', ')']


def t_LPAREN(t):
    r'\('
    t.type = 'LPAREN'
    return t

def t_RPAREN(t):
    r'\)'
    t.type = 'RPAREN'
    return t

def t_VARIABLE(t):
    r'[p-z][1-9]*[0-9]*'
    t.type = 'VARIABLE'
    return t

def t_CONJUNCTION(t):
    r'\^'
    t.type = 'CONJUNCTION'
    return t

def t_EQUIVALENCE(t):
    r'\='
    t.type = 'EQUIVALENCE'
    return t

def t_error(t):
    print("Unknown character \"{}\"".format(t.value[0]))
    t.lexer.skip(1)

def p_formula(p):
    """
    formula : atom
    formula : conjunction 
    formula : equivalence
    """
    p[0] = p[1]

def p_atom(p):
    """
    atom : VARIABLE
    """
    p[0] = Variable(letter=p[1])


def p_conjunction(p):
    """
    conjunction : LPAREN formula CONJUNCTION formula RPAREN
    """
    p[0] = Conjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_equivalence(p):
    """
    equivalence : LPAREN formula EQUIVALENCE formula RPAREN
    """
    p[0] = Equivalence(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False
    
def p_error(p):
    print(f"Error with: {p.value}")


def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == 'error'

def parse_pl_formula_infix_notation(text: str) -> Formula:
    lexer = lex.lex(reflags=re.UNICODE)
    lexer.input(text)
    for token in lexer:
        print(token)
    parser = yacc.yacc(write_tables=True)
    formula = yacc.parse(text)
    return formula



form = parse_pl_formula_infix_notation("(q = ((p ^ q) ^ p ))")
