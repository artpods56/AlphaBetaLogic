import re

from ply import lex, yacc

from .formula import (
    Conjunction,
    Disjunction,
    Equality,
    Formula,
    Implication,
    Negation,
    Variable,
)

tokens = [
    "LPAREN",
    "RPAREN",
    "VARIABLE",
    "CONJUNCTION",
    "EQUALITY",
    "NEGATION",
    "DISJUNCTION",
    "IMPLICATION",
]

t_ignore = " \t\r\n\f\v"

literals = ["(", ")"]


def t_LPAREN(t):
    r"\("
    t.type = "LPAREN"
    return t


def t_RPAREN(t):
    r"\)"
    t.type = "RPAREN"
    return t


def t_VARIABLE(t):
    r"[p-z]([1-9][0-9]*)?"
    t.type = "VARIABLE"
    return t


def t_CONJUNCTION(t):
    r"and"
    t.type = "CONJUNCTION"
    return t


def t_IMPLICATION(t):
    r"=>"
    t.type = "IMPLICATION"
    return t


def t_EQUALITY(t):
    r"<=>"
    t.type = "EQUALITY"
    return t


def t_NEGATION(t):
    r"~"
    t.type = "NEGATION"
    return t


def t_DISJUNCTION(t):
    r"or"
    t.type = "DISJUNCTION"
    return t


def t_error(t):
    print('Unknown character "{}"'.format(t.value[0]))
    t.lexer.skip(1)


def p_formula(p):
    """
    formula : atom
    formula : conjunction
    formula : equality
    formula : negation
    formula : negation_with_parens
    formula : disjunction
    formula : implication
    """
    p[0] = p[1]


def p_atom(p):
    """
    atom : VARIABLE
    """
    p[0] = Variable(letter=p[1])


def p_conjunction(p):
    """
    conjunction : LPAREN formula CONJUNCTION formula RPAREN
    """
    p[0] = Conjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_equality(p):
    """
    equality : LPAREN formula EQUALITY formula RPAREN
    """
    p[0] = Equality(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_negation(p):
    """
    negation : NEGATION formula
    """
    p[0] = Negation(arguments=[p[2]])
    p[2].is_self_standing = False


def p_negation_with_parens(p):
    """
    negation_with_parens : LPAREN NEGATION formula RPAREN
    """
    p[0] = Negation(arguments=[p[3]])
    p[3].is_self_standing = False


def p_implication(p):
    """
    implication : LPAREN formula IMPLICATION formula RPAREN
    """
    p[0] = Implication(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_disjunction(p):
    """
    disjunction : LPAREN formula DISJUNCTION formula RPAREN
    """
    p[0] = Disjunction(arguments=[p[2], p[4]])
    p[2].is_self_standing = False
    p[4].is_self_standing = False


def p_error(p):
    print("Syntax error in input!")


def __is_error(obj) -> bool:
    return isinstance(obj, yacc.YaccSymbol) and obj.type == "error"


def parse_formula(formula: str) -> Formula:
    lex.lex(reflags=re.UNICODE)
    yacc.yacc(write_tables=False)
    parsed_formula = yacc.parse(formula)
    parsed_formula.to_prefix_notation()
    return parsed_formula
