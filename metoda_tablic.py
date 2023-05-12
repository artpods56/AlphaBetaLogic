import re
import itertools
from ply import lex, yacc
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')
import random
import copy


class Formula:
    registry = set()

    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        Formula.registry.add(self)
        self.negation = False

    def to_prefix_notation(self):
        pass


class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        self.value = None
        self.exp = letter

    def to_prefix_notation(self):
        return self.letter

    def expand(self, beg):
        arg = self
        branch = [arg]
        return branch, [Vertex(beg, arg, self.exp)]


CONJUNCTION_PREFIX = "and"
NEGATION_PREFIX = "~"
EQUALITY_PREFIX = "<=>"
DISJUNCTION_PREFIX = "or"
IMPLICATION_PREFIX = "=>"


class Operator(Formula):
    def __init__(self, prefix: str, arguments: list):
        super().__init__()
        self.prefix = prefix
        self.arguments = arguments
        self.exp = None
        self.fork = self

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

    def expand(self):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        if self.negation == False:


            l_arg.fork = r_arg
            r_arg.fork = r_arg
            vertex_list = []
            for f in node.get_end(self.fork):
                l_copy = copy.copy(l_arg)
                l_arg.fork = l_copy
                r_copy = copy.copy(r_arg)
                r_arg.fork = r_copy
                vertex_list.extend([Vertex(f, l_copy, self.exp), Vertex(l_copy, r_copy, self.exp)])

            return vertex_list
        elif self.negation == True:
            self.arguments[0].negation = not self.arguments[0].negation
            self.arguments[1].negation = not self.arguments[1].negation
            l_arg = self.arguments[0]
            r_arg = self.arguments[1]
            l_arg.exp = "~" + l_arg.exp
            r_arg.exp = "~" + r_arg.exp

            vertex_list = []
            for f in node.get_end(self.fork):

                l_copy = copy.copy(l_arg)
                l_arg.fork = l_copy
                r_copy = copy.copy(r_arg)
                r_arg.fork = r_copy
                vertex_list.extend([Vertex(f, l_copy, self.exp), Vertex(f, r_copy, self.exp)])

            return vertex_list


class Disjunction(Operator):
    def __init__(self, arguments):
        super().__init__(DISJUNCTION_PREFIX, arguments)


class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments)

    def expand(self):
        if self.negation == False:
            #l_arg = copy.copy(self.arguments[0])
            #r_arg = copy.copy(self.arguments[1])
            self.arguments[0].negation = not self.arguments[0].negation
            nl_arg = self.arguments[0]
            r_arg = self.arguments[1]


            nl_arg.exp = "~" + nl_arg.exp


            end = [nl_arg,r_arg]
            #r_arg.fork = l_arg
            # return [[beg, l_arg],[l_arg,r_arg]]
            print(self.fork)
            vertex_list = []
            for f in self.fork:
                vertex_list.append([Vertex(f, nl_arg, self.exp), Vertex(f, copy.copy(r_arg), self.exp)])
            print("lista vertexow",vertex_list)
            return end,vertex_list
            #return end,[Vertex(self.fork, nl_arg, self.exp), Vertex(self.fork, r_arg, self.exp)]

        elif self.negation == True:
            l_arg = self.arguments[0]
            self.arguments[1].negation = not self.arguments[1].negation
            r_arg = self.arguments[1]
            r_arg.exp = "~" + r_arg.exp
            end = [r_arg]
            #l_arg.fork = r_arg
            #r_arg.fork = l_arg
            vertex_list = []
            for f in self.fork:
                l = copy.copy(l_arg)
                vertex_list.append(
                    [Vertex(f, l, self.exp), Vertex(l, copy.copy(r_arg), self.exp)])
            print("lista vertexow",vertex_list)
            return end,vertex_list
            #return end,[Vertex(self.fork, l_arg, self.exp), Vertex(l_arg, r_arg, self.exp)]


class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)

    def expand(self):
        if self.negation == False:
            #l_arg = copy.copy(self.arguments[0])
            #r_arg = copy.copy(self.arguments[1])
            l_arg = copy.copy(self.arguments[0])
            nl_arg = copy.copy(self.arguments[0])
            nl_arg.negation = not nl_arg.negation
            nl_arg.exp = "~" + nl_arg.exp

            r_arg = copy.copy(self.arguments[1])
            nr_arg = copy.copy(self.arguments[1])
            nr_arg.negation = not nr_arg.negation
            nr_arg.exp = "~" + nr_arg.exp

            self.arguments[0].fork = r_arg
            self.arguments[1].fork = nr_arg
            # self.arguments[1].negation = not self.arguments[1].negation
            # l_arg = self.arguments[0]
            #
            # self.arguments[0].negation = not self.arguments[0].negation
            # nl_arg = self.arguments[1]
            # nl_arg.exp = "~" + nl_arg.exp
            # l_arg.fork = r_arg
            # r_arg.fork = r_arg
            # return [[beg, l_arg],[l_arg,r_arg]]
            nl_arg.fork = nr_arg
            nr_arg.fork = nr_arg


            #self.arguments[1] = r_arg
            return [nl_arg,nr_arg],[Vertex(self.fork, l_arg, self.exp),
                                    Vertex(self.fork, nl_arg, self.exp),
                                    Vertex(l_arg, r_arg, self.exp),
                                    Vertex(nl_arg, nr_arg, self.exp)]

        elif self.negation == True:
            l_arg = copy.copy(self.arguments[0])
            nl_arg = copy.copy(self.arguments[0])
            nl_arg.negation = not nl_arg.negation
            nl_arg.exp = "~" + nl_arg.exp

            r_arg = copy.copy(self.arguments[1])
            nr_arg = copy.copy(self.arguments[1])
            nr_arg.negation = not nr_arg.negation
            nr_arg.exp = "~" + nr_arg.exp

            self.arguments[0].fork = r_arg
            self.arguments[1].fork = nr_arg
            # self.arguments[1].negation = not self.arguments[1].negation
            # l_arg = self.arguments[0]
            #
            # self.arguments[0].negation = not self.arguments[0].negation
            # nl_arg = self.arguments[1]
            # nl_arg.exp = "~" + nl_arg.exp
            # l_arg.fork = r_arg
            # r_arg.fork = r_arg
            # return [[beg, l_arg],[l_arg,r_arg]]
            nl_arg.fork = nr_arg
            nr_arg.fork = nr_arg


            #self.arguments[1] = r_arg
            return [nl_arg,nr_arg],[Vertex(self.fork, l_arg, self.exp),
                                    Vertex(self.fork, nl_arg, self.exp),
                                    Vertex(l_arg, nr_arg, self.exp),
                                    Vertex(nl_arg, r_arg, self.exp)]

class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)

    def to_prefix_notation(self):
        if isinstance(self.arguments[0], Variable):
            prefixed_argument = self.arguments[0].letter
        else:
            prefixed_argument = self.arguments[0].to_prefix_notation()

        self.exp = f"{self.prefix}{prefixed_argument}"
        return self.exp

    def expand(self, beg, value=False):
        pass
        # return self.arguments[0].expand(beg, value)


tokens = [
    "LPAREN",
    "RPAREN",
    "VARIABLE",
    "CONJUNCTION",
    "EQUALITY",
    "NEGATION",
    "DISJUNCTION",
    "IMPLICATION",
]

t_ignore = " \t\r\n\f\v"

literals = ["(", ")"]


def t_LPAREN(t):
    r"\("
    t.type = "LPAREN"
    return t


def t_RPAREN(t):
    r"\)"
    t.type = "RPAREN"
    return t


def t_VARIABLE(t):
    r"[p-z]([1-9][0-9]*)?"
    t.type = "VARIABLE"
    return t


def t_CONJUNCTION(t):
    r"and"
    t.type = "CONJUNCTION"
    return t


def t_IMPLICATION(t):
    r"=>"
    t.type = "IMPLICATION"
    return t


def t_EQUALITY(t):
    r"<=>"
    t.type = "EQUALITY"
    return t


def t_NEGATION(t):
    r"~"
    t.type = "NEGATION"
    return t


def t_DISJUNCTION(t):
    r"or"
    t.type = "DISJUNCTION"
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
    return isinstance(obj, yacc.YaccSymbol) and obj.type == "error"


def parse_pl_formula_infix_notation(text: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    formula.to_prefix_notation()
    return formula


def hierarchy_pos(G, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    """
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
    """
    if not nx.is_tree(G):
        raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(
                iter(nx.topological_sort(G))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(
            G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None
    ):
        """
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        """

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
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


# NKACE


class Node:
    def __init__(self, root):
        self.root = root
        self.connections = []
        self.branch = None
        self.stack = None
        self.fork = None
        self.graph = nx.Graph()
        self.labels = {}
        self.order = {
            "Negation": 0,
            "Variable": 1,
            "Conjunction": 2,
            "Disjunction": 3,
            "Implication": 4,
            "Equality": 5,
        }

    def sort(self, arguments):
        return sorted(arguments, key=lambda x: self.order[type(x).__name__])

    def create_stack(self):
        current_branch = self.branch
        self.branch = []
        # args = [x for x in argument.arguments]
        for arg in self.sort(current_branch):
            if not isinstance(arg, Variable):
                self.branch.extend(
                    self.sort([o for o in arg.arguments if not isinstance(o, Variable)])
                )
                self.stack.extend(
                    self.sort([o for o in arg.arguments if not isinstance(o, Variable)])
                )
        #
        if self.branch:
            self.create_stack()

    def clear(self, formula):
        for i, arg in enumerate(formula):
            while isinstance(formula[i], Negation):
                temp = formula[i].arguments[0]
                del formula[i]
                temp.negation = not temp.negation
                temp.exp = arg.exp
                formula.insert(i, temp)
            if not isinstance(arg, Variable):
                self.clear(arg.arguments)

        self.branch = formula
        self.stack = formula
        self.fork = copy.copy(formula)

    def grow(self):
        for i, arg in enumerate(self.stack):
            connections = self.stack[i].expand()
            self.connections.extend(connections)

    def find_leaf_nodes(self,graph, start_node):
        leaf_nodes = []
        successors = [x.end for x in graph if x.beg == start_node]
        print(successors)
        if len(successors) == 0:
            leaf_nodes.append(start_node)

        else:
            for successor in successors:
                #print(successor)
                leaf_nodes.extend(self.find_leaf_nodes(graph, successor))
        return leaf_nodes

    def get_end(self,fork):

        print("Do znalezienia: ",fork.exp)
        print("Polaczenia",self.connections)
        ends = self.find_leaf_nodes(self.connections,fork)
        #ends = [o.end for o in self.connections if fork == o.beg]
        print("Zwrocone", ends)
        return ends


    def display(self):
        def flatten(lst):
            """
            Recursively flattens a list of any depth.
            """
            result = []
            for item in lst:
                if isinstance(item, list):
                    result.extend(flatten(item))
                else:
                    result.append(item)
            return result
        # for o in self.connections:
        #     print("123", o)
        print(self.connections[0].end)
        connections = [[o.beg, o.end] for o in flatten(self.connections)]
        #connections = self.connections

        self.graph.add_edges_from(connections)
        for node in self.graph.nodes():
            self.labels[node] = node.exp

        options = {"edgecolors": "black", "node_size": 1200}
        pos = hierarchy_pos(self.graph, self.stack[0])
        #pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos=pos, with_labels=True, labels=self.labels, **options)
        plt.show()


class Vertex:
    def __init__(self, beg, end, exp):
        self.exp = exp
        self.beg = beg
        self.end = end


# f = parse_pl_formula_infix_notation("((p <=> ~q) and (~p <=> q))")
f = parse_pl_formula_infix_notation("(~((~(p and ~(p and q)) and ~(p and q)) and ~((~(p and ~((~(p and ~(p and q)) and ~(p and q)) and q)) and ~(p and q)) and q)) and ~(p and q))")
# print(check_if_tautology(f))
node = Node(f)
node.clear([f])

node.create_stack()
node.grow()
node.display()
# print(node.stack)
# %%