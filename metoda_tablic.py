import random
import re
import copy
from ply import lex, yacc
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')


class Formula:
    registry = set()
    counter = 0
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
        self.exp = letter
        self.color = '#2596be'

    def to_prefix_notation(self):
        return self.letter

    def negate(self):
        """
        Aplikuje negacje do zmiennej.
        """
        self.negation = not self.negation
        if self.exp[0] == '~':
            self.exp = self.exp[1:]
        else:
            self.exp = '~' + self.exp


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
        self.color = '#2596be'

    def to_prefix_notation(self):
        prefixed_arguments = list()
        for argument in self.arguments:
            if isinstance(argument, Variable):
                prefixed_arguments.append(argument.letter)
            else:
                prefixed_arguments.append(argument.to_prefix_notation())
        self.exp = f'({prefixed_arguments[0]} {self.prefix} {prefixed_arguments[1]})'
        return self.exp

    def negate(self):
        """
        Aplikuje negacje do wyrazenia.
        """
        self.negation = not self.negation
        if self.exp[0] == '~':
            self.exp = self.exp[1:]
        else:
            self.exp = '~' + self.exp


class Conjunction(Operator):
    def __init__(self, arguments):
        super().__init__(CONJUNCTION_PREFIX, arguments)

    def expand(self):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1

        if not self.negation:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(l_copy, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list
        else:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                r_copy.negate()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(f, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list


class Disjunction(Operator):
    def __init__(self, arguments):
        super().__init__(DISJUNCTION_PREFIX, arguments)

    def expand(self):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1
        if not self.negation:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(f, r_copy, f"{type(self).__name__} ({Formula.counter})")])
            return functors_list, vertex_list
        else:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                r_copy.negate()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(l_copy, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list


class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments)

    def expand(self):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1
        if not self.negation:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                # l_arg.fork, r_arg.fork = l_copy, r_copy
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(f, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list
        else:
            for f in tree.get_end(self):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                r_copy.negate()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(l_copy, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list


class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)

    def expand(self):
        l_arg = self.arguments[0]
        r_arg = self.arguments[1]
        nl_arg = copy.copy(l_arg)
        nr_arg = copy.copy(r_arg)

        vertex_list = []
        functors_list = []
        Formula.counter += 1
        if not self.negation:
            for f in tree.get_end(self):
                l_copy = copy.copy(l_arg)
                r_copy = copy.copy(r_arg)

                nl_copy = copy.copy(nl_arg)
                nr_copy = copy.copy(nr_arg)

                nl_copy.negate()
                nr_copy.negate()

                functors_list.extend([l_copy, nl_copy, r_copy, nr_copy])

                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(l_copy, r_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(f, nl_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(nl_copy, nr_copy, f"{type(self).__name__} ({Formula.counter})")])
            return functors_list, vertex_list
        else:
            for f in tree.get_end(self):
                l_copy = copy.copy(l_arg)
                r_copy = copy.copy(r_arg)

                nl_copy = copy.copy(nl_arg)
                nr_copy = copy.copy(nr_arg)

                nl_copy.negate()
                nr_copy.negate()

                functors_list.extend([l_copy, nl_copy, nr_copy, r_copy])

                vertex_list.extend([Vertex(f, l_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(l_copy, nr_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(f, nl_copy, f"{type(self).__name__} ({Formula.counter})"),
                                    Vertex(nl_copy, r_copy, f"{type(self).__name__} ({Formula.counter})")])

            return functors_list, vertex_list


class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)

    def to_prefix_notation(self):
        if isinstance(self.arguments[0], Variable):
            prefixed_argument = self.arguments[0].letter
        else:
            prefixed_argument = self.arguments[0].to_prefix_notation()

        self.exp = f'{self.prefix}{prefixed_argument}'
        return self.exp

    def expand(self, beg, value=False):
        pass


tokens = [
    'LPAREN',
    'RPAREN',
    'VARIABLE',
    'CONJUNCTION',
    'EQUALITY',
    'NEGATION',
    'DISJUNCTION',
    'IMPLICATION',
]

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
    '''
    formula : atom
    formula : conjunction
    formula : equality
    formula : negation
    formula : negation_with_parens
    formula : disjunction
    formula : implication
    '''
    p[0] = p[1]


def p_atom(p):
    '''
    atom : VARIABLE
    '''
    p[0] = Variable(letter=p[1])


def p_conjunction(p):
    '''
    conjunction : LPAREN formula CONJUNCTION formula RPAREN
    '''
    p[0] = Conjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_equality(p):
    '''
    equality : LPAREN formula EQUALITY formula RPAREN
    '''
    p[0] = Equality(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_negation(p):
    '''
    negation : NEGATION formula
    '''
    p[0] = Negation(arguments=[p[2]])
    p[2].is_self_standing = False


def p_negation_with_parens(p):
    '''
    negation_with_parens : LPAREN NEGATION formula RPAREN
    '''
    p[0] = Negation(arguments=[p[3]])
    p[3].is_self_standing = False


def p_implication(p):
    '''
    implication : LPAREN formula IMPLICATION formula RPAREN
    '''
    p[0] = Implication(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_disjunction(p):
    '''
    disjunction : LPAREN formula DISJUNCTION formula RPAREN
    '''
    p[0] = Disjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_error(p):
    print('Syntax error in input!')


def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == 'error'


def hierarchy_pos(G, root=None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
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
            root = next(
                iter(nx.topological_sort(G))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(
            G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None
    ):
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



class Vertex:
    """
    Klasa reprezentujaca polaczenie dwoch wezlow.

    Attributes
    ----------
        beg: object
            Poczatek wezla.
        end: object
            Koniec wezla.
        desc: str
            Opis wyrazenia znajdujacego sie w wezle.
    """
    def __init__(self, beg, end, desc):
        self.beg = beg
        self.end = end
        self.desc: str = desc


class Tree:
    """
    Klasa reprezentujaca obiekt przechowujacy informacje o wezlach oraz polaczeniach drzewa.

    Attributes
    ----------
    edges: list
        Lista polaczen.
    root: object
        Podstawa drzewa.
    stack: list
        Lista z ktorej pobierane sa wyrazenia do rozwiniecia.
    grap:
        Obiekt grafu biblioteki networkx.
    labels: dict
        Slownik zawierajacy oznaczenia wezlow.
    edge_labels: dict
        Slownik zawierajacy oznaczenia polaczen.
    color_map: list
        Lista zawierajaca zmapowana kolorystyke dla poszczegolnych wezlow.
    order: dict
        Kolejnosc w ktorej wyrazenia maja byc rozwijane.
    """
    def __init__(self):
        self.edges = []
        self.root = None
        self.stack = None
        self.graph = nx.Graph()
        self.labels = {}
        self.edge_labels = {}
        self.color_map = []
        self.order = {
            'Negation': 0,
            'Variable': 1,
            'Conjunction': 2,
            'Disjunction': 3,
            'Implication': 4,
            'Equality': 5,
        }

    def sort(self, arguments):
        return sorted(arguments, key=lambda x: self.order[type(x).__name__])

    def grow(self):
        """
        Rekursywnie rozloz wyrazenie wedlug regul metowy tablic analitycznych.
        """
        current_stack = self.stack
        self.stack = []
        for argument in current_stack:
            functors, connections = argument.expand()
            self.edges.extend(connections)
            self.stack.extend([o for o in functors if not isinstance(o, Variable)])

        if self.stack:
            self.grow()

    def clear(self, formula: Formula):
        """
        Oczysc strukture z pojedynczych oraz wielokrotynch negacji.

        Parameters
        ----------
        formula: object
            Wyrazenie krz w formie obiektu.
        """
        for i, arg in enumerate(formula):
            while isinstance(formula[i], Negation):
                temp = formula[i].arguments[0]
                del formula[i]
                temp.negation = not temp.negation
                temp.exp = arg.exp
                formula.insert(i, temp)
            if not isinstance(arg, Variable):
                self.clear(arg.arguments)

        self.stack = formula
        self.root = formula

    def find_leaf_nodes(self, edges: list, start_node) -> list:
        """
        Znajdz zakonczenia wychodzace z danego wezla.

        Parameters
        ----------
        edges : list
            Lista polaczen.
        start_node : object
            Wezel poczatkowy.

        Returns
        -------
        leaf_nodes: list
            Lista znalezionych wezlow.
        """

        leaf_nodes = []
        successors = [edge.end for edge in edges if edge.beg == start_node]
        if len(successors) == 0:
            leaf_nodes.append(start_node)

        else:
            for successor in successors:
                leaf_nodes.extend(self.find_leaf_nodes(edges, successor))
        return leaf_nodes

    def get_end(self, node) -> list:
        """

        """
        print('Do znalezienia: ', node.exp)
        found_nodes = self.find_leaf_nodes(self.edges, node)
        print('Zwrocone liście', [node.exp for node in found_nodes])
        return found_nodes

    def get_branch(self, end_node: object, set_color: bool) -> set:
        pairs = []
        connections_len = len(self.edges) - 1
        i = connections_len
        while i >= 0:
            if self.edges[i].end == end_node:
                if set_color == True:
                    self.edges[i].end.color = '#d77c2b'
                pairs.extend([self.edges[i].end.exp, self.edges[i].beg.exp])
                end_node = self.edges[i].beg
                i = connections_len
            i -= 1
        if set_color == True:
            self.edges[i + 1].beg.color = '#d77c2b'
        return set(pairs)

    def display(self):
        self.graph.add_edges_from([[o.beg, o.end] for o in self.edges])
        self.edge_labels = dict([((edge.beg, edge.end), edge.desc) for edge in self.edges])
        for node in self.graph.nodes():
            self.labels[node] = node.exp

        self.color_map = [node.color for node in self.graph]
        options = {'edgecolors': 'black', 'node_size': 1200}
        pos = hierarchy_pos(self.graph, self.root[0])
        #pos = nx.spring_layout(self.graph)

        nx.draw(self.graph,
                pos=pos,
                with_labels=True,
                node_color=self.color_map,
                labels=self.labels,
                **options)

        nx.draw_networkx_edge_labels(self.graph,
                                     pos=pos,
                                     edge_labels=self.edge_labels,
                                     label_pos=0.5,
                                     rotate=False,
                                     alpha=0.4,
                                     font_color='black',
                                     font_size=7,
                                     font_weight='bold')

        #plt.savefig("graph.png", format="PNG")
        plt.show()


def check_contradictions(expressions: list) -> bool:
    """
    Sprawdz, czy galaz zawiera wyrazenia sprzeczne.
    Parameters
    ----------
    expressions: list
        Lista wyrazen ktore zawiera galaz.

    Returns
    -------
    bool
        Zwroc True, jesli znajdziesz wyrazenia sprzeczne.
    """
    for expression in expressions:
        if expression[0] == '~':
            negation = expression[1:]
            if negation in expressions:
                print(f"Wyrażenia sprzeczne: {expression} oraz {negation}")
                return True
        else:
            negation = '~' + expression
            if negation in expressions:
                print(f"Wyrażenia sprzeczne: {expression} oraz {negation}")
                return True

    return False


def parse_pl_formula_infix_notation(text: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    formula.to_prefix_notation()
    return formula

def check_if_tautology(tree: Tree, formula: str) -> bool:
    """
    Sprawdz czy wyrazenie jest tautologia.

    Parameters
    ----------
    tree: Tree
        obiekt przechowujacy

    Returns
    -------
    bool
        zwroc True jesli wszystkie galezie zawieraja sprzecznosc.
    """
    parsed_formula = parse_pl_formula_infix_notation(formula)
    tree.clear([parsed_formula])
    tree.grow()
    print('_____________________________________')
    check = []
    for i, leaf in enumerate(tree.get_end(tree.root[0])):
        check.append(check_contradictions(tree.get_branch(leaf, False)))
        if check[i] == True:
            tree.get_branch(leaf, True)
        print(f'Branch nr. {i + 1} {check[i]} ')

    if all(check):
        return True
    else:
        return False

tautologies = [
               "~(p or ~p)", #prawo wylaczonego srodka
               "~(p <=> ~~p)", #prawo podwojnej negacji
               "~((p and (q or ~r)) => ((p and q) or (p and ~r)))",
               "~(~(p and q) <=> (~p or ~q))", #I prawo de Morgana
               "~(~(p or q) <=> (~p and ~q))", #II prawo de Morgana
               "~((p and (p => q)) => q)", #prawo odrywania
               "~(~(p => q) <=> (p and ~q))", #prawo negacji implikacji
               "~((p and (q or r)) <=> ((p and q) or (p and r)))", #prawo rozdzielnosci koniunkcji wzgledem alternatywy
               "~((p or (q and r)) <=> ((p or q) and (p or r)))", #prawo rozdzielnosci alternatywy wzgledem koniunkcji
               "~(((p => q) and (q => r)) => (p => r))", #prawo przechodnosci implikacji
               "~((q and p) => (q or p))"
               ]

for taut in tautologies:
    tree = Tree()
    Formula.counter = 0
    if check_if_tautology(tree,taut):
        print(f"Wyrażenie: {taut} jest tautologią.\n")
    else:
        print(f"Wyrażenie: {taut} nie jest tautologią.\n")
    tree.display()