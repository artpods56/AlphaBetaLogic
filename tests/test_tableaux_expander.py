import pytest

from alphabetalogic.formula import (Conjunction, Disjunction, Equality,
                                    Formula, Implication, Negation, Variable)
from alphabetalogic.parser import parse_formula
from alphabetalogic.tableaux import Tree
from alphabetalogic.tableaux_expander import TableauxExpander


class MockTree:
    """A mock Tree class for testing the TableauxExpander."""
    
    def __init__(self):
        self.edges = []
    
    def get_end(self, node):
        """Mock implementation that returns a list containing the node itself."""
        return [node]

def test_expander_conjunction():
    """Test expanding a conjunction formula."""
    # Parse a conjunction formula
    formula = parse_formula("(p and q)")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # p and q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the formula is not negated
    assert not formula.negation

def test_expander_negated_conjunction():
    """Test expanding a negated conjunction formula."""
    # Parse a conjunction formula and negate it
    formula = parse_formula("(p and q)")
    formula.negation = True
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # ~p and ~q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the functors are negated
    assert all(f.negation for f in functors)

def test_expander_disjunction():
    """Test expanding a disjunction formula."""
    # Parse a disjunction formula
    formula = parse_formula("(p or q)")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # p and q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the formula is not negated
    assert not formula.negation

def test_expander_negated_disjunction():
    """Test expanding a negated disjunction formula."""
    # Parse a disjunction formula and negate it
    formula = parse_formula("(p or q)")
    formula.negation = True
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # ~p and ~q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the functors are negated
    assert all(f.negation for f in functors)

def test_expander_implication():
    """Test expanding an implication formula."""
    # Parse an implication formula
    formula = parse_formula("(p => q)")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # ~p and q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the first functor is negated (for ~p)
    assert functors[0].negation
    
    # Verify the second functor is not negated (for q)
    assert not functors[1].negation

def test_expander_negated_implication():
    """Test expanding a negated implication formula."""
    # Parse an implication formula and negate it
    formula = parse_formula("(p => q)")
    formula.negation = True
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # p and ~q
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify the first functor is not negated (for p)
    assert not functors[0].negation
    
    # Verify the second functor is negated (for ~q)
    assert functors[1].negation

def test_expander_equality():
    """Test expanding an equality formula."""
    # Parse an equality formula
    formula = parse_formula("(p <=> q)")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 4  # p, ~p, q, ~q
    assert len(vertices) == 4  # Four vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify two functors are negated and two are not
    assert sum(1 for f in functors if f.negation) == 2
    assert sum(1 for f in functors if not f.negation) == 2

def test_expander_negated_equality():
    """Test expanding a negated equality formula."""
    # Parse an equality formula and negate it
    formula = parse_formula("(p <=> q)")
    formula.negation = True
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 4  # p, ~p, ~q, q
    assert len(vertices) == 4  # Four vertices connecting the nodes
    
    # Verify the functors are of the correct type
    assert all(isinstance(f, Variable) for f in functors)
    
    # Verify two functors are negated and two are not
    assert sum(1 for f in functors if f.negation) == 2
    assert sum(1 for f in functors if not f.negation) == 2

def test_expander_negation():
    """Test expanding a negation formula."""
    # Parse a negation formula
    formula = parse_formula("~p")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created no functors or vertices (negation doesn't expand)
    assert len(functors) == 0
    assert len(vertices) == 0

def test_expander_complex_formula():
    """Test expanding a complex formula."""
    # Parse a complex formula
    formula = parse_formula("((p and q) => (r or s))")
    
    # Create a mock tree
    tree = MockTree()
    
    # Create an expander with the mock tree
    expander = TableauxExpander(tree)
    
    # Expand the formula
    functors, vertices = expander.expand(formula)
    
    # Verify the expansion created the expected number of functors and vertices
    assert len(functors) == 2  # ~(p and q) and (r or s)
    assert len(vertices) == 2  # Two vertices connecting the nodes
    
    # Verify the first functor is a negated conjunction
    assert isinstance(functors[0], Conjunction) and functors[0].negation
    
    # Verify the second functor is a disjunction
    assert isinstance(functors[1], Disjunction) and not functors[1].negation


def test_clear_negations():
    formula = parse_formula("~~~(~~(p or r) and ~q)")
    expander = TableauxExpander(tree=None)
    print(type(formula),formula.negation)
    cleaned_formula = expander.clear([formula]) 
    print(cleaned_formula[0].__dict__)
    assert cleaned_formula[0].arguments[0].negation == False

expander = TableauxExpander(None) # Instantiate expander once for all tests

class TestClearNegations:

    def test_single_negation(self):
        formula = parse_formula("~p")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True
        assert cleaned_formula[0].exp == "p"

    def test_double_negation(self):
        formula = parse_formula("~~p")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == False
        assert cleaned_formula[0].exp == "p"

    def test_triple_negation(self):
        formula = parse_formula("~~~p")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True
        assert cleaned_formula[0].exp == "p"

    def test_nested_negations(self):
        formula = parse_formula("~~~~~~p") # 6 negations
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == False
        assert cleaned_formula[0].exp == "p"
        formula = parse_formula("~~~~~p") # 5 negations
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True
        assert cleaned_formula[0].exp == "p"

    def test_negation_and_or_no_demorgan(self):
        formula = parse_formula("~(p or q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True # Negation remains at the OR level - no De Morgan yet
        assert cleaned_formula[0].prefix == "or"
        assert not cleaned_formula[0].arguments[0].negation
        assert not cleaned_formula[0].arguments[1].negation


    def test_negation_and_and_no_demorgan(self):
        formula = parse_formula("~(p and q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True # Negation remains at the AND level - no De Morgan yet
        assert cleaned_formula[0].prefix == "and"
        assert not cleaned_formula[0].arguments[0].negation
        assert not cleaned_formula[0].arguments[1].negation

    def test_double_negation_and_or(self):
        formula = parse_formula("~~(p or q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == False # Negation cancelled out
        assert cleaned_formula[0].prefix == "or"
        assert not cleaned_formula[0].arguments[0].negation
        assert not cleaned_formula[0].arguments[1].negation

    def test_negated_and_with_negated_vars(self):
        formula = parse_formula("~(~p and ~q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True # Negation remains at the AND level - no De Morgan yet
        assert cleaned_formula[0].prefix == "and"
        assert cleaned_formula[0].arguments[0].negation == True # Negation of p and q preserved within
        assert cleaned_formula[0].arguments[1].negation == True

    def test_complex_nested_negations_and_or(self):
        formula = parse_formula("~~~(~~(p or r) and ~q)") # Original test case
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == True # Outer negation remains after simplifying triple negations to single
        assert cleaned_formula[0].prefix == "and"
        assert cleaned_formula[0].arguments[0].prefix == "or"
        assert not cleaned_formula[0].arguments[0].arguments[0].negation # p should not be negated
        assert not cleaned_formula[0].arguments[0].arguments[1].negation # r should not be negated
        assert cleaned_formula[0].arguments[1].negation == True # q should still be negated

    def test_no_negations_simple_and(self):
        formula = parse_formula("(p and q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == False
        assert cleaned_formula[0].prefix == "and"
        assert not cleaned_formula[0].arguments[0].negation
        assert not cleaned_formula[0].arguments[1].negation

    def test_no_negations_simple_or(self):
        formula = parse_formula("(p or q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0].negation == False
        assert cleaned_formula[0].prefix == "or"
        assert not cleaned_formula[0].arguments[0].negation
        assert not cleaned_formula[0].arguments[1].negation

    def test_already_cleaned_formula(self):
        formula = parse_formula("(p or q)")
        cleaned_formula = expander.clear([formula])
        assert cleaned_formula[0] == formula # Should return the same formula if already cleaned


