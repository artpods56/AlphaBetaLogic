import re
import itertools
from ply import lex, yacc
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import random


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
        self.value = None

    def to_prefix_notation(self):
        return self.letter


CONJUNCTION_PREFIX = 'and'
NEGATION_PREFIX = '~'
EQUALITY_PREFIX = '<=>'
DISJUNCTION_PREFIX = 'or'
IMPLICATION_PREFIX = '=>'


class Operator(Formula):
    def __init__(self, prefix: str, arguments: list):
        super().__init__()
        self.prefix = prefix
        self.arguments = arguments
        self.exp = None

    def to_prefix_notation(self):
        prefixed_arguments = list()
        for argument in self.arguments:
            if isinstance(argument, Variable):
                prefixed_arguments.append(argument.letter)
            else:
                prefixed_arguments.append(argument.to_prefix_notation())
        self.exp = f"({prefixed_arguments[0]} {self.prefix} {prefixed_arguments[1]})"
        return self.exp


class Conjunction(Operator):
    def __init__(self, arguments):
        super().__init__(CONJUNCTION_PREFIX, arguments)

    def expand(self, beg):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        # return [[beg, l_arg],[l_arg,r_arg]]
        return [Vertex(beg, l_arg, self.exp), Vertex(l_arg, r_arg, self.exp)]


class Disjunction(Operator):
    def __init__(self, arguments):
        super().__init__(DISJUNCTION_PREFIX, arguments)


class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments)


class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)


class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)


tokens = ['LPAREN', 'RPAREN', 'VARIABLE', 'CONJUNCTION', 'EQUALITY', 'NEGATION', 'DISJUNCTION', 'IMPLICATION']

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
    formula.to_prefix_notation()
    return formula


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike

    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


# NKACE


class Node:
    def __init__(self, root):
        self.root = root
        self.connections = []
        self.stack = []
        self.graph = nx.Graph()
        self.labels = {}
        self.order = {"Variable": 0, "Conjunction": 1, "Disjunction": 2, "Implication": 3, "Equality": 4}

    def grow(self, argument):
        if argument == None:
            argument = self.root

        vertex_list = argument.expand(self.root)
        for o in vertex_list:
            self.connections.append(o)
        args = [x for x in argument.arguments]
        self.stack.append(sorted(args, key=lambda x: self.order[type(x).__name__]))

        # for o in sorted_args:
        #     self.grow(o)
        # if not self.connections:
        #     base = Vertex(formula.arguments[0],formula.arguments[1])
        # else:
        #     base = self.connections[-1][-1]
        # branch = Vertex(formula.arguments[1],object)
        # pair = [base,branch]
        # for o in pair:
        #     self.connections.append([o.beg,o.end])

    def pop_stack(self):
        pass

    def display(self):
        self.graph.add_edges_from([[o.beg, o.end] for o in self.connections])
        for node in self.graph.nodes():
            self.labels[node] = node.exp

        options = {"edgecolors": "black", "node_size": 1200}
        pos = hierarchy_pos(self.graph, self.root)
        nx.draw(self.graph, pos=pos, with_labels=True, labels=self.labels, **options)


class Vertex:
    def __init__(self, beg, end, exp):
        self.exp = exp
        self.beg = beg
        self.end = end


f = parse_pl_formula_infix_notation('((p <=> q) and (p => q) )')

# print(check_if_tautology(f))
node = Node(f)

# node.grow(None)
# node.display()