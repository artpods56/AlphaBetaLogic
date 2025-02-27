import copy

from ply import lex, yacc

from .utils import Vertex


class Formula:
    registry = set()
    counter = 0

    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        Formula.registry.add(self)
        self.negation = False

    def get_value(self):
        pass

    @staticmethod
    def set_values(variables_dict):
        for f in Formula.registry:
            if isinstance(f, Variable):
                f.set_value(variables_dict[f.letter])

    def to_prefix_notation(self):
        pass


class Variable(Formula):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter
        self.exp = letter
        self.color = "#2596be"

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def to_prefix_notation(self):
        return self.letter

    def negate(self):
        """Neguje zmienna."""
        self.negation = not self.negation
        if self.exp[0] == "~":
            self.exp = self.exp[1:]
        else:
            self.exp = "~" + self.exp


CONJUNCTION_PREFIX = "and"
NEGATION_PREFIX = "~"
EQUALITY_PREFIX = "<=>"
DISJUNCTION_PREFIX = "or"
IMPLICATION_PREFIX = "=>"


class Operator(Formula):
    def __init__(self, prefix: str, arguments: list):
        super().__init__()
        self.prefix = prefix
        self.arguments = arguments
        self.exp = None
        self.color = "#2596be"

    def to_prefix_notation(self):
        prefixed_arguments = list()
        for argument in self.arguments:
            if isinstance(argument, Variable):
                prefixed_arguments.append(argument.letter)
            else:
                prefixed_arguments.append(argument.to_prefix_notation())
        self.exp = f"({prefixed_arguments[0]} {self.prefix} {prefixed_arguments[1]})"
        return self.exp

    def negate(self):
        """Neguje wyrazenie."""
        self.negation = not self.negation
        if self.exp[0] == "~":
            self.exp = self.exp[1:]
        else:
            self.exp = "~" + self.exp


class Conjunction(Operator):
    def __init__(self, arguments):
        super().__init__(CONJUNCTION_PREFIX, arguments)

    def get_value(self):
        return self.arguments[0].get_value() and self.arguments[1].get_value()


class Disjunction(Operator):
    def __init__(self, arguments):
        super().__init__(DISJUNCTION_PREFIX, arguments)

    def get_value(self):
        return self.arguments[0].get_value() or self.arguments[1].get_value()


class Implication(Operator):
    def __init__(self, arguments):
        super().__init__(IMPLICATION_PREFIX, arguments)

    def get_value(self):
        if self.arguments[0].get_value() == 0 or self.arguments[1].get_value() == 1:
            return 1
        else:
            return 0


class Equality(Operator):
    def __init__(self, arguments):
        super().__init__(EQUALITY_PREFIX, arguments)

    def get_value(self):
        return int(self.arguments[0].get_value() == self.arguments[1].get_value())


class Negation(Operator):
    def __init__(self, arguments):
        super().__init__(NEGATION_PREFIX, arguments)

    def get_value(self):
        return int(not (self.arguments[0].get_value()))

    def to_prefix_notation(self):
        if isinstance(self.arguments[0], Variable):
            prefixed_argument = self.arguments[0].letter
        else:
            prefixed_argument = self.arguments[0].to_prefix_notation()

        self.exp = f"{self.prefix}{prefixed_argument}"
        return self.exp
