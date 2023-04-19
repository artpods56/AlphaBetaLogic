import re
import itertools
from ply import lex, yacc
import itertools
import copy

class Formula():
    registry = set()
    variables_dict = None
    sprzecznosc = False

    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        self.comb = [(True,False),(False,True),(False,False),(True,True)]
        Formula.registry.add(self)   
        self.branch = []
        self.value = None
    def generate_possible_solutions(self,values):
       return list(itertools.product(*[[False, True] if value is None else [value] for value in values]))
     
    def set_variables(self,variables):
        Formula.variables_dict = variables
        print(f'Zainicjalizowano zmiennymi: {self.variables_dict}')
    
    def gen_values(self,func_value):
        status = []
        self.value = func_value
        for l in self.arguments:
            if isinstance(l,Variable): #and l.variables_dict[l.letter] !=:
                #print(l.letter,l.variables_dict[l.letter])
                status.append(l.variables_dict[l.letter])
            else:
                status.append(None)
        #print("lewa i prawa",left,right)
        pairs = self.generate_possible_solutions(status)
        print(f"Status: {status}\nWygenerowano: {pairs} \nWartosc funktora: {func_value}")
        combs = self.get_pairs(pairs)
        if self.is_self_standing or func_value == False:
            self.values = set(combs)
        elif func_value == True:
            self.values = set(pairs) - set(combs)
            
        print(type(self).__name__,self.values,"\n")
        if len(self.values) == 0:
            Formula.sprzecznosc = True
        for val in self.values:
            leaf = copy.deepcopy(self)
            for i, f in enumerate(leaf.arguments):
                
                if isinstance(f, Variable):
                    f.set_value(val[i])
                else:
                    f.gen_values(val[i])
            self.branch.append(leaf)
            

   

class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        self.value = None
   
   
    def set_value(self, value):
        self.value = value
        #if Formula.variables_dict[self.letter] == None:
        Formula.variables_dict[self.letter] = value
        print(f"Zmienna zaktualizowana {self.letter}: {value}")
        # elif Formula.variables_dict[self.letter] == value:
        #     print("Spojnosc zmiennych")
        # elif Formula.variables_dict[self.letter] != value:
        #     print("Sprzecznosc zmiennych")
        #     Formula.sprzecznosc == True
            
        
       
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
       

class Conjunction(Operator):
    def __init__(self, arguments):
        super().__init__(CONJUNCTION_PREFIX, arguments)
   
    def get_pairs(self,pairs):
        return [x for x in self.comb if not(x[0] and x[1])]
        

class Disjunction(Operator):
    def __init__(self, arguments):
        self.values = None
        super().__init__(DISJUNCTION_PREFIX, arguments)
   
    def get_pairs(self,pairs):
        return [x for x in pairs if not(x[0] or x[1])]
        

class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments)
        
    def get_pairs(self,pairs):
        return [x for x in pairs if not x[0] and x[1]]
        

class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)
   
    def get_pairs(self,pairs):
        return [x for x in self.comb if not(x[0] == x[1])]
   
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
        Formula.set_values(variables_dict)
        result = f.get_value()
        print(f'{variables_dict} => {result}')
        results.append(result)
       
    return all(results)




def short_check(f: Formula) -> bool:
    variables = {o.letter: None for o in f.registry if isinstance(o, Variable)}
    f.set_variables(variables)
    
    f.gen_values(False)
    if f.sprzecznosc:
        print("Jest tautologia")
    else:
        print("Nie jest tautologia")
    
f = parse_pl_formula_infix_notation('(p <=> q)')

short_check(f)
