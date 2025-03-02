import pytest

from alphabetalogic.formula import (Conjunction, Disjunction, Equality,
                                    Formula, Implication, Negation, Variable)
from alphabetalogic.parser import parse_formula
from alphabetalogic.tableaux import Tree
from alphabetalogic.tableaux_expander import TableauxExpander


def test_expand_implication():
    
    logical_expression = "(p => q)"
    tree = Tree()
    parsed_expression = parse_formula(logical_expression)
    tableaux_expander = TableauxExpander(tree)
    tableaux_expander.stack = [parsed_expression]
    tableaux_expander.grow()

    for vertex in tableaux_expander.edges:
        print(vertex.__dict__)
