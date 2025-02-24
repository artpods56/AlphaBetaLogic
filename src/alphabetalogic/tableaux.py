import re

import matplotlib.pyplot as plt
import networkx as nx
from ply import lex, yacc

from .formula import Formula, Variable
from .utils import hierarchy_pos
from .utils import Vertex


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
            "Negation": 0,
            "Variable": 1,
            "Conjunction": 2,
            "Disjunction": 3,
            "Implication": 4,
            "Equality": 5,
        }

    def sort(self, arguments):
        return sorted(arguments, key=lambda x: self.order[type(x).__name__])

    def grow(self):
        """
        Rekursywnie rozloz wyrazenie wedlug regul metody tablic analitycznych.
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
        """ """
        # print('Do znalezienia: ', node.exp)
        found_nodes = self.find_leaf_nodes(self.edges, node)
        # print('Zwrocone liście', [node.exp for node in found_nodes],"\n")
        return found_nodes

    def get_branch(self, end_node: object, set_color: bool) -> set:
        pairs = []
        connections_len = len(self.edges) - 1
        i = connections_len
        while i >= 0:
            if self.edges[i].end == end_node:
                if set_color:
                    self.edges[i].end.color = "#d77c2b"
                pairs.extend([self.edges[i].end.exp, self.edges[i].beg.exp])
                end_node = self.edges[i].beg
                i = connections_len
            i -= 1
        if set_color:
            self.edges[i + 1].beg.color = "#d77c2b"
        return set(pairs)

    def display(self):
        self.graph.add_edges_from([[o.beg, o.end] for o in self.edges])
        self.edge_labels = dict(
            [((edge.beg, edge.end), edge.desc) for edge in self.edges]
        )
        for node in self.graph.nodes():
            self.labels[node] = node.exp

        self.color_map = [node.color for node in self.graph]

        options = {"edgecolors": "black", "node_size": 1200}
        pos = hierarchy_pos(self.graph, self.root[0])
        # pos = nx.spring_layout(self.graph)

        nx.draw(
            self.graph,
            pos=pos,
            with_labels=True,
            node_color=self.color_map,
            labels=self.labels,
            **options,
        )

        nx.draw_networkx_edge_labels(
            self.graph,
            pos=pos,
            edge_labels=self.edge_labels,
            label_pos=0.5,
            rotate=False,
            alpha=0.4,
            font_color="black",
            font_size=7,
            font_weight="bold",
        )

        # plt.savefig("graph.png", format="PNG")
        plt.show()


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
        if expression.startswith("~"):
            negation = expression[1:]
            if negation in expressions:
                print(f"Wyrażenia sprzeczne: {expression} oraz {negation}")
                return True
        else:
            negation = "~" + expression
            if negation in expressions:
                print(f"Wyrażenia sprzeczne: {expression} oraz {negation}")
                return True
    print("Brak wyrazen sprzecznych.")
    return False


def parse_pl_formula_infix_notation(text: str) -> Formula:
    tree = Tree()
    lex.lex(reflags=re.UNICODE)
    yacc.yacc(write_tables=False)
    formula = yacc.parse(text)
    print(formula.__dict__)
    formula.to_prefix_notation()
    return formula


def check_if_tautology(formula: str) -> bool:
    """
    Sprawdz czy wyrazenie jest tautologia.

    Parameters
    ----------
    tree: Tree
        Obiekt przechowujacy informacje o wezlach i polaczeniach.
    formula: str
        Wyrazenie krz w formie napisu.
    Returns
    -------
    bool
        Zwroc True jesli wszystkie galezie zawieraja sprzecznosc.
    """

    parsed_formula = parse_pl_formula_infix_notation(formula)
    tree.clear([parsed_formula])
    tree.grow()
    check = []
    for i, leaf in enumerate(tree.get_end(tree.root[0])):
        check.append(check_contradictions(tree.get_branch(leaf, False)))
        if check[i]:
            tree.get_branch(leaf, True)
        print(f"Galaz numer. {i + 1} {check[i]} ")

    if all(check):
        return True
    else:
        return False


def check_with_table(formula: str) -> bool:
    print("\nMetoda tablic: ")
    f = parse_pl_formula_infix_notation(formula[1:])
    variables = sorted(set({o.letter for o in f.registry if isinstance(o, Variable)}))
    all_01_combinations = list(itertools.product([0, 1], repeat=len(variables)))
    results = list()
    for combination in all_01_combinations:
        variables_dict = {k: v for k, v in zip(variables, combination)}
        Formula().set_values(variables_dict)
        result = f.get_value()
        print(f"{variables_dict} => {result}")
        results.append(result)

    return all(results)


tautologies = [
    "~(p or ~p)",  # prawo wylaczonego srodka
    "~(p <=> ~~p)",  # prawo podwojnej negacji
    "~((p and (q or ~r)) <=> ((p and q) or (p and ~r)))",
    "~(~(p and q) <=> (~p or ~q))",  # I prawo de Morgana
    "~(~(p or q) <=> (~p and ~q))",  # II prawo de Morgana
    "~((p and (p => q)) => q)",  # prawo odrywania
    "~(~(p => q) <=> (p and ~q))",  # prawo negacji implikacji
    "~((p and (q or r)) <=> ((p and q) or (p and r)))",  # prawo rozdzielnosci koniunkcji wzgledem alternatywy
    "~((p or (q and r)) <=> ((p or q) and (p or r)))",  # prawo rozdzielnosci alternatywy wzgledem koniunkcji
    "~(((p => q) and (q => r)) => (p => r))",  # prawo przechodnosci implikacji
    "~((q and p) => (q or p))",
]
#for taut in tautologies:




#print(check_if_tautology("~(p or ~p)"))
#while True:
#    taut = input("insert tautology")
#    print("________________________________")
#    print(f"Sprawdzane wyrażenie: {taut}")
#    Formula.counter = 0
#
#    tree = Tree()
#    checked_tree = check_if_tautology(tree,taut)
#    checked_tables = check_with_table(taut)
#
#    if checked_tables and checked_tree:
#        print(f"Wyrażenie: {taut} jest tautologią.\n")
#    else:
#        print(f"Wyrażenie: {taut} nie jest tautologią.\n")
    #tree.display()