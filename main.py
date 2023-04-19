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

CONJUNCTION_PREFIX = 'C'


class Conjunction(Formula):
    def __init__(self, arguments: list):
        super().__init__()
        self.arguments = arguments
        
    def to_prefix_notation(self):
        prefixed_arguments = list()
        for argument in self.arguments:
            if isinstance(argument, Variable):
                prefixed_arguments.append(argument.letter)
            else:
                prefixed_arguments.append(argument.to_prefix_notation())
        return ''.join([CONJUNCTION_PREFIX] + prefixed_arguments)


import re
from ply import lex, yacc

tokens = ['L_KLAMRA','P_KLAMRA','ZMIENNA', 'FUNKTOR']

t_ignore = ' \t\r\n\f\v'

literals = ['(', ')']


def t_L_KLAMRA(t):
    r'\('
    t.type = 'L_KLAMRA'
    return t

def t_P_KLAMRA(t):
    r'\)'
    t.type = 'P_KLAMRA'
    return t

def t_ZMIENNA(t):
    r'[p-z][1-9]*[0-9]*'
    t.type = 'ZMIENNA'
    return t

def t_FUNKTOR(t):
    r'<=>'
    t.type = 'FUNKTOR'
    return t

def p_formula(p):
    """
    formula : atom
    formula : funktor
    """
    p[0] = p[1]

def p_atom(p):
    """
    atom : ZMIENNA
    """
    p[0] = Variable(letter=p[1])


def p_FUNKTOR(p):
    """
    funktor : L_KLAMRA formula FUNKTOR formula P_KLAMRA
    """
    p[0] = Conjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False

def p_error(p):
    print("Syntax error in input!")

def t_error(p):
    print("No coś nie działą")
def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == 'error'

def parse_pl_formula_infix_notation(text: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    parser = yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    return formula
  
  
parse_pl_formula_infix_notation("(q<=>p)")