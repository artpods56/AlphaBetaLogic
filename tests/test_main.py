import copy
import os

import pytest
from test_utils.load_test_samples import load_logical_expressions

from alphabetalogic.formula import Formula, Negation
from alphabetalogic.parser import parse_formula
from alphabetalogic.tableaux import Tree, Vertex, check_contradictions
from alphabetalogic.tableaux_expander import TableauxExpander
from alphabetalogic.utils import negate_expression


def check_tautology(logical_expression: str) -> bool:
    """
    Check if a logical expression is a tautology using the tableau method.
    
    A formula F is a tautology if and only if ~F is unsatisfiable.
    We negate the formula and build a tableau. If all branches close (contain contradictions),
    then the original formula is a tautology.
    
    Parameters
    ----------
    logical_expression : str
        The logical expression to check.
        
    Returns
    -------
    bool
        True if the expression is a tautology, False otherwise.
    """
    print(f"\nChecking if '{logical_expression}' is a tautology...")
    
    # Step 1: Parse the formula
    parsed_formula: Formula = parse_formula(logical_expression)
    print(f"Parsed formula: {parsed_formula.exp} (type: {type(parsed_formula).__name__})")
    
    # Step 2: Negate the formula to check if it's a tautology
    negated_formula = Negation(arguments=[parsed_formula])
    negated_formula.to_prefix_notation()
    print(f"Negated formula: {negated_formula.exp}")
    
    # Step 3: Initialize the tableau tree
    tree = Tree()
    tree.root = [negated_formula]
    
    # Step 4: Clean the formula (remove double negations)
    cleaned_formula = tree.expander.clear([negated_formula])
    print(f"Cleaned formula: {[f.exp for f in cleaned_formula]}")
    
    # Step 5: Set the initial stack for expansion
    tree.stack = cleaned_formula
    tree.grow()
    
    # Step 7: Check for contradictions in each branch
    all_branches_closed = True
    leaf_nodes = tree.get_end(tree.root[0])
    print(f"Number of branches: {len(leaf_nodes)}")
    
    for i, leaf in enumerate(leaf_nodes):
        branch = tree.get_branch(leaf, False)
        print(f"Branch {i+1} contents: {branch}")
        has_contradiction = check_contradictions(branch)
        if has_contradiction:
            tree.get_branch(leaf, True)  # Color the branch if contradictory
        else:
            all_branches_closed = False
        print(f"Branch number {i + 1}: {'closed' if has_contradiction else 'open'}")
    
    # If all branches have contradictions, the original formula is a tautology
    result = all_branches_closed
    print(f"Is '{logical_expression}' a tautology? {result}")
    return result


@pytest.mark.parametrize("logical_expression", load_logical_expressions())
def test_check_logical_expressions(logical_expression): 
    """
    Test that expressions in the test file are correctly identified as tautologies.
    """
    # Check if the expression is a tautology
    is_tautology = check_tautology(logical_expression)
    
    # All expressions in the test file should be tautologies
    assert is_tautology, f"The formula {logical_expression} should be a tautology"
