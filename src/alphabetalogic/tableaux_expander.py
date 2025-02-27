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

    def clear(self, formulas: List[Formula]):
        """
        Oczysc strukture z pojedynczych oraz wielokrotynch negacji.

        Parameters
        ----------
        formula: object
            Wyrazenie krz w formie obiektu.
        """

        for i in range(len(formulas)):
            while isinstance(formulas[i],Negation):
                print(formulas[i].exp)
                
                inner = formulas[i].arguments[0]
                print(f"switching from {formulas[i].arguments[0].negation} to {not formulas[i].arguments[0].negation}")
                formulas[i].arguments[0].negation = not formulas[i].negation
                formulas[i] = formulas[i].arguments[0]
            print(f"formula {formulas[i].exp} has {formulas[i].negation}")
            if not isinstance(formulas[i],Variable):
                self.clear(formulas[i].arguments)

        return formulas


    def clear(self, formulas: List[Formula]):
        for i in range(len(formulas)):
            while isinstance(formulas[i], Negation):
                outer = formulas[i]
                inner = outer.arguments[0]
                inner.negation = not outer.negation
                formulas[i] = inner
            if not isinstance(formulas[i], Variable):
                self.clear(formulas[i].arguments)
        return formulas

    #    for i, arg in enumerate(formula):
    #        while isinstance(formula[i], Negation):
    #            temp = formula[i].arguments[0]
    #            del formula[i]
    #            temp.negation = not temp.negation
    #            temp.exp = arg.exp
    #            formula.insert(i, temp)
    #        if not isinstance(arg, Variable):
    #            self.clear(arg.arguments)

    #    return formula

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
            return [], []  # Negation doesn't expand in the current implementation
        else:
            return [], []  # Default case for other formula types

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
