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



import ply.lex as lex

tokens = (
   'ZMIENNA',
   'ROWNOWAZNOSC',
   'KONIUNKCJA',
   #'L_KLAMRA',
   #'P_KLAMRA',
)

literals = ("(",
            ")")

t_ROWNOWAZNOSC    = r'\='
t_KONIUNKCJA   = r'\^'
#t_L_KLAMRA  = r'\('
#t_P_KLAMRA  = r'\)'


def t_ZMIENNA(t):
    r'[p-z][1-9]*[0-9]*'
    return t

def p_formula(p):
    """
    formula : atom
    formula : funktor
    """
    p[0] = p[1]
    
def t_FUNKTOR(t):
    pass

def p_atom(p):
    """
    atom : ZMIENNA
    """
    p[0] = Variable(letter=p[1])


def p_FUNKTOR(p):
    """
    funktor : formula FUNKTOR formula
    """
    p[0] = Conjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False
t_ignore = ' \t\r\n\f\v'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    return False
    t.lexer.skip(1)


lexer = lex.lex()






lexer.input("(q = p)")
for token in lexer:
    print(token)
