import copy
import itertools
import random
import re

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from ply import lex, yacc

from utils import hierarchy_pos

matplotlib.use("TkAgg")




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




print(check_if_tautology("~(p or ~p)"))
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
#%%

tree = Tree()
