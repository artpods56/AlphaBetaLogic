import os

import pytest

from alphabetalogic.tableaux import Tree, check_if_tautology
from alphabetalogic.tests.test_utils import load_logical_expressions


@pytest.mark.parametrize("logical_expression", load_logical_expressions())
def test_check_logical_expressions(logical_expression):
    tree = Tree()

    print(logical_expression)
    print(negate_expression((logical_expression)))
    assert check_if_tautology(negate_expression(logical_expression))
