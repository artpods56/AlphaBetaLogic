import os

import pytest
from test_utils.load_test_samples import load_logical_expressions

from alphabetalogic.formula import Formula
from alphabetalogic.parser import parse_formula
from alphabetalogic.tableaux import Tree, check_if_tautology
from alphabetalogic.tableaux_expander import TableauxExpander
from alphabetalogic.utils import negate_expression


@pytest.mark.parametrize("logical_expression", load_logical_expressions())
def test_check_logical_expressions(logical_expression): 
    parsed_formula: Formula = parse_formula(logical_expression)
    tree = Tree()
    cleaned_formula = tree.clear([parsed_formula])
    tableaux_expander = TableauxExpander(tree)
    tableaux_expander.expand(cleaned_formula) 
    assert check_if_tautology(negate_expression(logical_expression))
