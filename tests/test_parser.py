import pytest
from test_utils.load_test_samples import load_logical_expressions

from alphabetalogic.formula import Formula
from alphabetalogic.parser import parse_formula


@pytest.mark.parametrize("logical_expression", load_logical_expressions())
def test_parser_return(logical_expression):
    parsed_sample = parse_formula(logical_expression)
    assert isinstance(parsed_sample, Formula)
