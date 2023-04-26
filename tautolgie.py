import re
import itertools
from ply import lex, yacc
import itertools
import copy

class Tree:
    def __init__(self):
        self.core = []
        
    def build_tree(self,formula):
        temp = []
        for i, l in enumerate(formula.leafs):
            temp.append([l])
            for arg in l.arguments:
                if not isinstance(arg, Variable) and len(arg.leafs)>1:
                    temp[i].append(self.build_tree(arg))
                else:
                    temp[i].append(arg)
            #temp[i].append([[arg] if not  else arg for arg in l.arguments])
            #temp.append(self.build_tree(l))
        self.core = temp
        
    
    
    def test(self,formula):
        for l in formula.leafs:
            print(l)
        if len(formula.leafs) == 1:
            return formula.leafs[0]
        return [[l] for l in formula.leafs]
    
    def insert_object(self,leafs):
        if not self.core:
            for o in leafs:
                self.core.append([o])
        else:
            self.update_branchs(self.core, leafs)

    def update_branchs(self,branch,leafs):
        c = 0
        for b in branch:
            if isinstance(b, list):
                c += 1
                self.update_branchs(b,leafs)
        if c == 0:
            if len(leafs) == 1:
                branch.append(leafs[0])
            else:
                branch.append([[l] for l in leafs])
                
    def update_dicts(self,var_dict):
        pass
            
                
tree = Tree()

class Formula():
    registry = set()
    
    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        self.comb = [(True,False),(False,True),(False,False),(True,True)]
        Formula.registry.add(self)   
        
        self.value = None
        self.values = None
        self.variables_dict = None
        self.status = []
        self.flag = False
        
    def generate_possible_solutions(self,values):
       return list(itertools.product(*[[False, True] if value is None else [value] for value in values]))
     
    def set_variables(self,variables):
        vars_copy = copy.copy(variables)
        self.variables_dict = vars_copy
        if not isinstance(self, Variable):
            for obj in self.arguments:
                obj.set_variables(vars_copy)
    
    def set_all(self,letter,value):     
        if isinstance(self, Variable) and self.letter == letter:
            self.set_value(value)
            return
        else:
            for o in self.arguments:
                if not isinstance(o, (Variable,Negation)):
                    o.set_all(letter,value)
    
    def get_variables(self):
        return self.variables_dict
    
    def gen_values(self,func_value):

        #print(f"Status: {status}\nWygenerowano: {pairs} \nWartosc funktora: {self.value}")
        #print(f"Slownik: {self.variables_dict}")
        combs = self.get_pairs(self.comb)
        
        if self.is_self_standing or func_value == False:
            self.values = set(combs)
        elif func_value == True:
            self.values = set(self.comb) - set(combs)
            

        self.value = func_value
        self.status = []
        for l in self.arguments:
            # if len(self.status) == 2:
            #     break
            if isinstance(l,Variable) and l.variables_dict[l.letter] != None:
                self.status.append(l.variables_dict[l.letter])
                continue
            else:
                self.status.append(None)
                continue
        pairs = self.generate_possible_solutions(self.status)        
        
        
        
        
        self.values = [val for val in self.values if val in pairs]
        if not self.values:
            return self.variables_dict
        leafs = [copy.deepcopy(self) for leaf in self.values]
        print(self.status)
        print([[type(l).__name__, val] for l, val in zip(leafs,self.values)])
        self.leafs = leafs
        
        #print(type(self).__name__,self.status, [l.letter for l in self.arguments if isinstance(l, Variable)], self.variables_dict)
        for val,leaf in zip(self.values,leafs):
            
            leaf.values = val
            

            #if val not in pairs:
            #    continue
            #print(type(leaf).__name__,leaf.status,val)
            objects = [[value,obj] for value,obj in zip(val,leaf.arguments)]
            sorted_arguments = sorted(objects, key=lambda f: not isinstance(f[1], Variable))
            
            for pack in sorted_arguments:
                val, arg = pack[0], pack[1]
                if isinstance(arg, Variable):
                    self.variables_dict = arg.set_value(val)
                    if all(value is not None for value in arg.variables_dict.values()) and self.flag == False:
                        self.flag = True
                        print(f"Flaga zmieniona {arg.variables_dict}")
                    self.set_variables(self.variables_dict)
                    
                    leaf.set_all(arg.letter,val)
                    #print(leaf.variables_dict)
                else:

                    # else:
                    if self.flag == False:
                        arg.set_variables(self.variables_dict)
                        
                    self.variables_dict = arg.gen_values(val)
                    #updated_variables = arg.gen_values(val)
                    #arg.set_variables(vals)
        return self.variables_dict    

    

class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        self.value = None
        self.variables_dict = None
   
    def set_value(self, value):
        self.value = value
        backup = self.variables_dict
        if self.variables_dict[self.letter] == None:
            self.variables_dict[self.letter] = value

        return self.variables_dict
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
        return [x for x in pairs if not(x[0] and x[1])]
        

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
        return [x for x in pairs if x[0] and not x[1]]
        

class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)
   
    def get_pairs(self,pairs):
        return [x for x in pairs if not(x[0] == x[1])]
   
class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)
   
    def gen_values(self,func_value):
       
        self.value = func_value 
        if isinstance(self.arguments[0],Variable):
            self.arguments[0].set_value(not func_value)
        else:
            self.arguments[0].gen_values(not func_value)
   
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
    tree.build_tree(f)
    
    
f = parse_pl_formula_infix_notation("((q and p) => ((q or r) => r))")
#f = parse_pl_formula_infix_notation("((p or q) <=> r)")
#f = parse_pl_formula_infix_notation("((p and (q or ~r)) => ((p and q) or (p and ~r)))")
short_check(f)