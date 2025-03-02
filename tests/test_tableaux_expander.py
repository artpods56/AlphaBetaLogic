import pytest

from alphabetalogic.formula import (Conjunction, Disjunction, Equality,
                                    Implication, Negation, Variable)
from alphabetalogic.tableaux import Tree
from alphabetalogic.tableaux_expander import TableauxExpander
from alphabetalogic.utils import Vertex


@pytest.fixture
def test_variables():
    return [
        Variable(letter="p"),
        Variable(letter="q"),
    ]

@pytest.fixture
def tableaux_expander():
    tree = Tree()
    return TableauxExpander(tree)


class TestOperatorExpander:
    """
    Tests the expansion of logical operators within the tableaux framework.
    
    This test suite verifies that the TableauxExpander correctly expands various logical operators 
    such as Implication, Conjunction, Disjunction, and Equality. The expansion should create the appropriate 
    nodes and branches within the tableaux structure, ensuring correct logical transformations.
    
    Used notation:
    - A, B represent any logical formulas.
    - ~ represents negation.
    - ∧ represents conjunction (and).
    - ∨ represents disjunction (or).
    - => represents implication.
    - <=> represents equivalence.
    """


    def test_implication(self, test_variables, tableaux_expander):
        """
        Implication (A => B):
            ┌──────────┐
            │  A => B  │
            └────┬─────┘
              ┌──┴──┐
              │     │
             ~A     B
        """
        implication = Implication(arguments=test_variables)
        tableaux_expander.stack = [implication]
        tableaux_expander.grow()

        assert len(tableaux_expander.nodes) == 2, "Implication should create exactly 2 nodes"

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        assert alpha_edge.beg == beta_edge.beg, "Both nodes should branch from the same parent node"

        assert all([isinstance(node.end, Variable) for node in [alpha_edge,beta_edge]]), "Both nodes should end with Variable objects"

        assert alpha_edge.end.negation, "First branch should contain a negated variable"

        assert not beta_edge.end.negation, "Second branch should contain a non-negated variable"

    def test_negated_implication(self, test_variables, tableaux_expander):
        """
        Negated Implication ~(A => B):
            ┌──────────┐
            │~(A => B) │
            └────┬─────┘
                 │
                 A
                 │
                ~B
        """
        implication = Implication(arguments=test_variables)
        implication.negation = True
        tableaux_expander.stack = [implication]
        tableaux_expander.grow()

        assert len(tableaux_expander.nodes) == 2

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        assert alpha_edge.end == beta_edge.beg, "Nodes should share the same parent"

        assert isinstance(alpha_edge.end, Variable)
        assert alpha_edge.end.letter == "p"
        assert not alpha_edge.end.negation

        assert isinstance(beta_edge.end, Variable)
        assert beta_edge.end.letter == "q"
        assert beta_edge.end.negation

    def test_conjunction(self, test_variables, tableaux_expander):
        """
        Conjunction (A ∧ B):
            ┌──────────┐
            │  A ∧ B   │
            └────┬─────┘
                 │
                 A
                 │
                 B
        """
        conjunction = Conjunction(arguments=test_variables)
        tableaux_expander.stack = [conjunction]
        tableaux_expander.grow()

        # should have two nodes in same branch
        assert len(tableaux_expander.nodes) == 2, "Conjunction should create exactly 2 nodes"

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        # verify the tree structure: alpha_edge.end == beta_edge.beg (connected in same branch)
        assert alpha_edge.end == beta_edge.beg, "Nodes should form a linear branch (second node connected to first)"

        # first node should be p
        assert isinstance(alpha_edge.end, Variable)
        assert alpha_edge.end.letter == "p"
        assert not alpha_edge.end.negation

        # second node should be q
        assert isinstance(beta_edge.end, Variable)
        assert beta_edge.end.letter == "q"
        assert not beta_edge.end.negation

    def test_negated_conjunction(self, test_variables, tableaux_expander):
        """
        Negated Conjunction ~(A ∧ B):
            ┌──────────┐
            │~(A or B) │
            └────┬─────┘
              ┌──┴──┐
              │     │
             ~A    ~B
        """
        conjunction = Conjunction(arguments=test_variables)
        conjunction.negation = True
        tableaux_expander.stack = [conjunction]
        tableaux_expander.grow()

        # should have two nodes in separate branches
        assert len(tableaux_expander.nodes) == 2, "Negated conjunction should create exactly 2 nodes"

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        # linked nodes have same parent node
        assert alpha_edge.beg == beta_edge.beg, "Both nodes should branch from the same parent (branching structure)"

        # both ends are Variables
        assert isinstance(alpha_edge.end, Variable)
        assert isinstance(beta_edge.end, Variable)

        # both ends should be negated
        assert alpha_edge.end.negation, "First variable should be negated"
        assert beta_edge.end.negation, "Second variable should be negated"

        # verify the variables
        assert alpha_edge.end.letter == "p", "First branch should contain variable 'p'"
        assert beta_edge.end.letter == "q", "Second branch should contain variable 'q'"

    def test_disjunction(self, test_variables, tableaux_expander):
        """
        Disjunction (A ∨ B):
            ┌──────────┐
            │  A or B  │
            └────┬─────┘
              ┌──┴──┐
              │     │
              A     B
        """
        disjunction = Disjunction(arguments=test_variables)
        tableaux_expander.stack = [disjunction]
        tableaux_expander.grow()

        # should have two nodes in separate branches
        assert len(tableaux_expander.nodes) == 2

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        # linked nodes have same parent node
        assert alpha_edge.beg == beta_edge.beg

        # both ends are Variables
        assert isinstance(alpha_edge.end, Variable)
        assert isinstance(beta_edge.end, Variable)

        # both ends should not be negated
        assert not alpha_edge.end.negation
        assert not beta_edge.end.negation

        # verify the variables
        assert alpha_edge.end.letter == "p"
        assert beta_edge.end.letter == "q"

    def test_negated_disjunction(self, test_variables, tableaux_expander):
        """
        Negated Disjunction ~(A ∨ B):
            ┌──────────┐
            │~(A or B) │
            └────┬─────┘
                 │
                ~A
                 │
                ~B
        """
        disjunction = Disjunction(arguments=test_variables)
        disjunction.negation = True
        tableaux_expander.stack = [disjunction]
        tableaux_expander.grow()

        # should have two nodes in same branch
        assert len(tableaux_expander.nodes) == 2

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        # verify the tree structure: alpha_edge.end == beta_edge.beg (connected in same branch)
        assert alpha_edge.end == beta_edge.beg

        # first node should be negated p
        assert isinstance(alpha_edge.end, Variable)
        assert alpha_edge.end.letter == "p"
        assert alpha_edge.end.negation

        # second node should be negated q
        assert isinstance(beta_edge.end, Variable)
        assert beta_edge.end.letter == "q"
        assert beta_edge.end.negation

    def test_equality(self, test_variables, tableaux_expander):
        """
        Equality (A <=> B):
            ┌──────────┐
            │  A <=> B │
            └────┬─────┘
              ┌──┴──┐
              │     │
              A    ~A
              │     │
              B    ~B
        """
        equality = Equality(arguments=test_variables)
        tableaux_expander.stack = [equality]
        tableaux_expander.grow()

        # should have 4 nodes: 2 branches with 2 nodes each
        assert len(tableaux_expander.nodes) == 4, "Equality should create 4 nodes (2 branches with 2 nodes each)"

        # First branch: p and q
        branch1_edge1: Vertex = tableaux_expander.nodes[0]
        branch1_edge2: Vertex = tableaux_expander.nodes[1]

        # Second branch: ~p and ~q
        branch2_edge1: Vertex = tableaux_expander.nodes[2]
        branch2_edge2: Vertex = tableaux_expander.nodes[3]

        # Verify tree structure for first branch
        assert branch1_edge1.end == branch1_edge2.beg, "First branch should form a linear path"

        # Verify tree structure for second branch
        assert branch2_edge1.end == branch2_edge2.beg, "Second branch should form a linear path"

        # First branch should have p and q (not negated)
        assert isinstance(branch1_edge1.end, Variable)
        assert branch1_edge1.end.letter == "p"
        assert not branch1_edge1.end.negation

        assert isinstance(branch1_edge2.end, Variable)
        assert branch1_edge2.end.letter == "q"
        assert not branch1_edge2.end.negation

        # Second branch should have ~p and ~q (negated)
        assert isinstance(branch2_edge1.end, Variable)
        assert branch2_edge1.end.letter == "p"
        assert branch2_edge1.end.negation

        assert isinstance(branch2_edge2.end, Variable)
        assert branch2_edge2.end.letter == "q"
        assert branch2_edge2.end.negation

    def test_negated_equality(self, test_variables, tableaux_expander):
        """
        Negated Equivalence ~(A <=> B):
            ┌──────────┐
            │~(A <=> B)│
            └────┬─────┘
              ┌──┴──┐
              │     │
              A    ~A
              │     │
             ~B     B
        """
        equality = Equality(arguments=test_variables)
        equality.negation = True
        tableaux_expander.stack = [equality]
        tableaux_expander.grow()

        # should have 4 nodes: 2 branches with 2 nodes each
        assert len(tableaux_expander.nodes) == 4, "Negated equality should create 4 nodes (2 branches with 2 nodes each)"

        # First branch: p and ~q
        branch1_edge1: Vertex = tableaux_expander.nodes[0]
        branch1_edge2: Vertex = tableaux_expander.nodes[1]

        # Second branch: ~p and q
        branch2_edge1: Vertex = tableaux_expander.nodes[2]
        branch2_edge2: Vertex = tableaux_expander.nodes[3]

        # Verify tree structure for first branch
        assert branch1_edge1.end == branch1_edge2.beg, "First branch should form a linear path"

        # Verify tree structure for second branch
        assert branch2_edge1.end == branch2_edge2.beg, "Second branch should form a linear path"

        # First branch should have p (not negated) and ~q (negated)
        assert isinstance(branch1_edge1.end, Variable)
        assert branch1_edge1.end.letter == "p"
        assert not branch1_edge1.end.negation

        assert isinstance(branch1_edge2.end, Variable)
        assert branch1_edge2.end.letter == "q"
        assert branch1_edge2.end.negation

        # Second branch should have ~p (negated) and q (not negated)
        assert isinstance(branch2_edge1.end, Variable)
        assert branch2_edge1.end.letter == "p"
        assert branch2_edge1.end.negation

        assert isinstance(branch2_edge2.end, Variable)
        assert branch2_edge2.end.letter == "q"
        assert not branch2_edge2.end.negation


@pytest.fixture
def test_variable():
    return Variable(letter="p")


class TestNegationElimination:
    def test_single_negation(self, test_variable, tableaux_expander):
        negation = Negation(arguments=[test_variable])
        # clearing the formula should return Variable with applied Negation
        cleaned_formula = tableaux_expander.clear([negation])[0]
        assert cleaned_formula.negation, "Single negation should result in a negated variable"
        assert isinstance(cleaned_formula, Variable), "Result should be a Variable, not a Negation object"
        assert cleaned_formula.letter == test_variable.letter, "Variable letter should be preserved"

    def test_double_negation(self, test_variable, tableaux_expander):
        negation = Negation(arguments=[test_variable])
        double_negation = Negation(arguments=[negation])
        # should return Variable with negation completely eliminated
        cleaned_formula = tableaux_expander.clear([double_negation])[0]
        assert not cleaned_formula.negation, "Double negation should cancel out and result in non-negated variable"
        assert isinstance(cleaned_formula, Variable), "Result should be a Variable, not a Negation object"
        assert cleaned_formula.letter == test_variable.letter, "Variable letter should be preserved"

    def test_triple_negation(self, test_variable, tableaux_expander):
        negation = Negation(arguments=[test_variable])
        double_negation = Negation(arguments=[negation])
        triple_negation = Negation(arguments=[double_negation])
        # should return negated Variable because two implications are eliminated and the even one is applied
        cleaned_formula = tableaux_expander.clear([triple_negation])[0]
        assert cleaned_formula.negation, "Triple negation should result in a negated variable (odd number of negations)"
        assert isinstance(cleaned_formula, Variable), "Result should be a Variable, not a Negation object"
        assert cleaned_formula.letter == test_variable.letter, "Variable letter should be preserved"

    def test_single_formula(self, test_variables, tableaux_expander):
        formula = Implication(arguments=test_variables)
        negated_formula = Negation(arguments=[formula])
        # should return Implication with applied negation
        cleaned_formula = tableaux_expander.clear([negated_formula])[0]
        assert cleaned_formula.negation, "Single negation should be applied to the formula"
        assert isinstance(cleaned_formula, Implication), "Result should maintain the original formula type"
        assert cleaned_formula == formula, "Formula structure should be preserved"

    def test_nested_formula(self, test_variables, tableaux_expander):
        formula = Implication(arguments=test_variables)
        negated_formula = Negation(arguments=[formula])
        double_negated_formula = Negation(arguments=[negated_formula])
        # should return Implication with negation completely eliminated
        cleaned_formula = tableaux_expander.clear([double_negated_formula])[0]
        assert not cleaned_formula.negation, "Double negation should cancel out"
        assert isinstance(cleaned_formula, Implication), "Result should maintain the original formula type"
        assert cleaned_formula == formula, "Formula structure should be preserved"


class TestParametrizedOperators:
    @pytest.mark.parametrize(
        "operator_class,negated,expected_nodes,expected_structure,expected_negations",
        [
            # (operator class, negated, node count, structure, negation states)
            (Conjunction, False, 2, "linear", [False, False]),  # p ∧ q → p, q (linear)
            (Conjunction, True, 2, "branching", [True, True]),  # ¬(p ∧ q) → ¬p | ¬q (branching)
            (Disjunction, False, 2, "branching", [False, False]),  # p ∨ q → p | q (branching)
            (Disjunction, True, 2, "linear", [True, True]),  # ¬(p ∨ q) → ¬p, ¬q (linear)
            (Implication, False, 2, "branching", [True, False]),  # p → q = ¬p | q (branching)
            (Implication, True, 2, "linear", [False, True]),  # ¬(p → q) = p, ¬q (linear)
        ],
    )
    def test_operator_expansion(
        self, test_variables, tableaux_expander,
        operator_class, negated, expected_nodes, expected_structure, expected_negations
    ):
        formula = operator_class(arguments=test_variables)
        formula.negation = negated
        tableaux_expander.stack = [formula]
        tableaux_expander.grow()

        assert len(tableaux_expander.nodes) == expected_nodes

        alpha_edge: Vertex = tableaux_expander.nodes[0]
        beta_edge: Vertex = tableaux_expander.nodes[1]

        # Check structure
        if expected_structure == "linear":
            assert alpha_edge.end == beta_edge.beg, "Expected linear structure (second node connected to first)"
        else:  # branching
            assert alpha_edge.beg == beta_edge.beg, "Expected branching structure (nodes share parent)"
            assert alpha_edge.end != beta_edge.beg, "Expected separate branches"

        # Check variable types and negation states
        assert isinstance(alpha_edge.end, Variable), "First node should be a Variable"
        assert isinstance(beta_edge.end, Variable), "Second node should be a Variable"
        assert alpha_edge.end.negation == expected_negations[0], f"First variable negation should be {expected_negations[0]}"
        assert beta_edge.end.negation == expected_negations[1], f"Second variable negation should be {expected_negations[1]}"

        # Verify letter values
        assert alpha_edge.end.letter == "p", "First variable should be 'p'"
        assert beta_edge.end.letter == "q", "Second variable should be 'q'"
