import copy
from typing import List

from .formula import (Conjunction, Disjunction, Equality, Formula, Implication,
                      Negation, Operator, Variable)
from .utils import Vertex


class TableauxExpander:
    """
    Class responsible for expanding formulas according to the rules of the analytical tableaux method.
    This decouples the expansion logic from the formula classes.
    """

    def __init__(self, tree):
        """
        Initialize the expander with a reference to the tableaux tree.

        Parameters
        ----------
        tree : Tree
            The tableaux tree that will be used for expansion.
        """
        self.tree = tree
        self.stack = None
        self.nodes = []

    def clear(self, formulas: List[Formula]):
        """
        Oczysc strukture z pojedynczych oraz wielokrotynch negacji.

        Parameters
        ----------
        formula: object
            Wyrazenie krz w formie obiektu.
        """

        for i in range(len(formulas)):
            while isinstance(formulas[i], Negation):
                outer = formulas[i]
                inner = outer.arguments[0]
                inner.negation = not outer.negation
                formulas[i] = inner
            if not isinstance(formulas[i], Variable):
                self.clear(formulas[i].arguments)
        return formulas
    
    def grow(self):
        """
        Recursively decompose the expression according to the rules of the analytical tableaux method.
        """
        current_stack = self.stack
        self.stack = []
        for argument in current_stack:
            functors, new_nodes = self.expand(argument)  # Use the expander
            self.nodes.extend(new_nodes)
            self.stack.extend([o for o in functors if not isinstance(o, Variable)])

        if self.stack:
            self.grow()
    
    def expand(self, formula):
        """
        Expand a formula according to its type and the rules of the analytical tableaux method.

        Parameters
        ----------
        formula : Formula
            The formula to expand.

        Returns
        -------
        tuple
            A tuple containing (functors_list, vertex_list).
        """
        if isinstance(formula, Conjunction):
            return self._expand_conjunction(formula)
        elif isinstance(formula, Disjunction):
            return self._expand_disjunction(formula)
        elif isinstance(formula, Implication):
            return self._expand_implication(formula)
        elif isinstance(formula, Equality):
            return self._expand_equality(formula)
        elif isinstance(formula, Negation):
            return self._expand_negation(formula)
        else:
            return [], []  # Default case for other formula types
            
    def _expand_negation(self, formula):
        """
        Expand a negation formula.
        
        For negations of complex formulas, we transform them according to logical equivalences:
        ~(A and B) -> ~A or ~B
        ~(A or B) -> ~A and ~B
        ~(A => B) -> A and ~B
        ~(A <=> B) -> (A and ~B) or (~A and B)
        ~~A -> A
        
        For simple negations like ~p, we just pass them through.
        """
        inner_arg = formula.arguments[0]
        
        # If the inner formula is already a Variable, we don't expand further
        if isinstance(inner_arg, Variable):
            return [], []
        
        # For other types, we negate the inner formula and expand it according to its type
        if isinstance(inner_arg, Conjunction):
            # ~(A and B) -> ~A or ~B
            inner_arg.negation = True
            return self._expand_conjunction(inner_arg)
            
        elif isinstance(inner_arg, Disjunction):
            # ~(A or B) -> ~A and ~B
            inner_arg.negation = True
            return self._expand_disjunction(inner_arg)
            
        elif isinstance(inner_arg, Implication):
            # ~(A => B) -> A and ~B
            inner_arg.negation = True
            return self._expand_implication(inner_arg)
            
        elif isinstance(inner_arg, Equality):
            # ~(A <=> B) -> (A and ~B) or (~A and B)
            inner_arg.negation = True
            return self._expand_equality(inner_arg)
            
        elif isinstance(inner_arg, Negation):
            # ~~A -> A (double negation elimination)
            return self.expand(inner_arg.arguments[0])
            
        return [], []  # Default case

    def _expand_conjunction(self, formula):
        """Expand a conjunction formula."""
        l_arg = formula.arguments[0]
        r_arg = formula.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1

        if not formula.negation:
            # Regular conjunction: (A and B) -> A, B on the same branch
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                # Make sure to update the expressions
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            l_copy,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
        else:
            # Negated conjunction: ~(A and B) -> ~A or ~B on separate branches
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                r_copy.negate()
                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            f,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )

        return functors_list, vertex_list

    def _expand_disjunction(self, formula):
        """Expand a disjunction formula."""
        l_arg = formula.arguments[0]
        r_arg = formula.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1

        if not formula.negation:
            # Regular disjunction: (A or B) -> A or B on separate branches
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                # Make sure to update the expressions
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            f,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list
        else:
            # Negated disjunction: ~(A or B) -> ~A and ~B on the same branch
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                r_copy.negate()
                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            l_copy,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list

    def _expand_implication(self, formula):
        """Expand an implication formula."""
        l_arg = formula.arguments[0]
        r_arg = formula.arguments[1]
        vertex_list = []
        functors_list = []
        Formula.counter += 1

        if not formula.negation:
            # Regular implication: (A => B) -> ~A or B on separate branches
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                l_copy.negate()
                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            f,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list
        else:
            # Negated implication: ~(A => B) -> A and ~B on the same branch
            for f in self.tree.get_end(formula):
                l_copy, r_copy = copy.copy(l_arg), copy.copy(r_arg)
                r_copy.negate()
                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                functors_list.extend([l_copy, r_copy])
                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            l_copy,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list

    def _expand_equality(self, formula):
        """Expand an equality formula."""
        l_arg = formula.arguments[0]
        r_arg = formula.arguments[1]
        nl_arg = copy.copy(l_arg)
        nr_arg = copy.copy(r_arg)

        vertex_list = []
        functors_list = []
        Formula.counter += 1

        if not formula.negation:
            # Regular equality: (A <=> B) -> (A and B) or (~A and ~B)
            for f in self.tree.get_end(formula):
                l_copy = copy.copy(l_arg)
                r_copy = copy.copy(r_arg)

                nl_copy = copy.copy(nl_arg)
                nr_copy = copy.copy(nr_arg)

                nl_copy.negate()
                nr_copy.negate()

                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                nl_copy.to_prefix_notation()
                nr_copy.to_prefix_notation()

                functors_list.extend([l_copy, nl_copy, r_copy, nr_copy])

                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            l_copy,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            f,
                            nl_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            nl_copy,
                            nr_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list
        else:
            # Negated equality: ~(A <=> B) -> (A and ~B) or (~A and B)
            for f in self.tree.get_end(formula):
                l_copy = copy.copy(l_arg)
                r_copy = copy.copy(r_arg)

                nl_copy = copy.copy(nl_arg)
                nr_copy = copy.copy(nr_arg)

                nl_copy.negate()
                nr_copy.negate()

                # Make sure to update the expressions after negation
                l_copy.to_prefix_notation()
                r_copy.to_prefix_notation()
                nl_copy.to_prefix_notation()
                nr_copy.to_prefix_notation()

                functors_list.extend([l_copy, nl_copy, nr_copy, r_copy])

                vertex_list.extend(
                    [
                        Vertex(
                            f,
                            l_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            l_copy,
                            nr_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            f,
                            nl_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                        Vertex(
                            nl_copy,
                            r_copy,
                            f"{type(formula).__name__} ({Formula.counter}) \n {formula.exp}",
                        ),
                    ]
                )
            return functors_list, vertex_list
