import re
import itertools
from ply import lex, yacc


class Formula():
    registry = set()

    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        Formula.registry.add(self)

    def get_value(self):
        pass

    def to_prefix_notation(self):
        pass

    @staticmethod
    def set_values(variables_dict):
        for f in Formula.registry:
            if isinstance(f, Variable):
                f.set_value(variables_dict[f.letter])

class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        self.value = None

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def to_prefix_notation(self):
        return self.letter

CONJUNCTION_PREFIX = 'C'
NEGATION_PREFIX = 'N'
EQUALITY_PREFIX = 'E'
DISJUNCTION_PREFIX = 'D'
IMPLICATION_PREFIX = 'I'

class Operator(Formula):
    def __init__(self, prefix: str, arguments: list):
        super().__init__()
        self.prefix = prefix
        self.arguments = arguments

    def to_prefix_notation(self):
        prefixed_arguments = list()
        for argument in self.arguments:
            if isinstance(argument, Variable):
                prefixed_arguments.append(argument.letter)
            else:
                prefixed_arguments.append(argument.to_prefix_notation())
        return ''.join([self.prefix] + prefixed_arguments)

class Conjunction(Operator):
    def __init__(self, arguments):
        super().__init__(CONJUNCTION_PREFIX, arguments)

    def get_value(self):
        return self.arguments[0].get_value() and self.arguments[1].get_value()

class Disjunction(Operator):
    def __init__(self, arguments):
        super().__init__(DISJUNCTION_PREFIX, arguments)

    def get_value(self):
        return self.arguments[0].get_value() or self.arguments[1].get_value()

class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments, huj)

    def get_value(self):
        if self.arguments[0].get_value() == 0 or self.arguments[1].get_value() == 1:
            return 1
        else:
            return 0

class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)

    def get_value(self):
        return int(self.arguments[0].get_value() == self.arguments[1].get_value())

class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)

    def get_value(self):
        return int(not(self.arguments[0].get_value()))


tokens = ['LPAREN','RPAREN','VARIABLE', 'CONJUNCTION', 'EQUALITY', 'NEGATION', 'DISJUNCTION', 'IMPLICATION']

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
    r'[p-z]([1-9][0-9]*)?'
    t.type = 'VARIABLE'
    return t

def t_CONJUNCTION(t):
    r'and'
    t.type = 'CONJUNCTION'
    return t

def t_IMPLICATION(t):
    r'=>'
    t.type = 'IMPLICATION'
    return t

def t_EQUALITY(t):
    r'<=>'
    t.type = 'EQUALITY'
    return t

def t_NEGATION(t):
    r'~'
    t.type = 'NEGATION'
    return t

def t_DISJUNCTION(t):
    r'or'
    t.type = 'DISJUNCTION'
    return t


def t_error(t):
    print('Unknown character "{}"'.format(t.value[0]))
    t.lexer.skip(1)

def p_formula(p):
    """
    formula : atom
    formula : conjunction
    formula : equality
    formula : negation
    formula : negation_with_parens
    formula : disjunction
    formula : implication
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

def p_equality(p):
    """
    equality : LPAREN formula EQUALITY formula RPAREN
    """
    p[0] = Equality(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False

def p_negation(p):
    """
    negation : NEGATION formula
    """
    p[0] = Negation(arguments=[p[2]])
    p[2].is_self_standing = False

def p_negation_with_parens(p):
    """
    negation_with_parens : LPAREN NEGATION formula RPAREN
    """
    p[0] = Negation(arguments=[p[3]])
    p[3].is_self_standing = False

def p_implication(p):
    """
    implication : LPAREN formula IMPLICATION formula RPAREN
    """
    p[0] = Implication(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False

def p_disjunction(p):
    """
    disjunction : LPAREN formula DISJUNCTION formula RPAREN
    """
    p[0] = Disjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False

def p_error(p):
    print("Syntax error in input!")

def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == 'error'

def parse_pl_formula_infix_notation(text: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    return formula

def check_if_tautology(f: Formula) -> bool:
    variables = sorted(set({o.letter for o in f.registry if isinstance(o, Variable)}))
    all_01_combinations = list(itertools.product([0, 1], repeat=len(variables)))
    results = list()
    for combination in all_01_combinations:
        variables_dict = {k: v for k, v in zip(variables, combination)}
        Formula().set_values(variables_dict)
        result = f.get_value()
        print(f'{variables_dict} => {result}')
        results.append(result)

    return all(results)

f = parse_pl_formula_infix_notation('((p and (q or ~r)) <=> ((p and q) or (p and ~r)))')


print(check_if_tautology(f))