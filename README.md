# AlphaBetaLogic Parser Library

A Python library for parsing and analyzing logical expressions using the PLY (Python Lex-Yacc) library.

## Introduction

AlphaBetaLogic is a tool for parsing, representing, and analyzing logical expressions. It provides a robust parser for propositional logic formulas and implements the analytical tableaux method for checking if a formula is a tautology.

### Features

- Parse logical expressions into a structured representation
- Support for variables, negation, conjunction, disjunction, implication, and equality
- Implementation of the analytical tableaux method for tautology checking
- Visualization of tableaux trees using NetworkX and Matplotlib

### Installation

```bash
pip install alphabetalogic
```

Or install from source:

```bash
git clone https://github.com/yourusername/ply_parsing_tool.git
cd ply_parsing_tool
pip install -e .
```

## Parser Module

The parser module (`parser.py`) is responsible for parsing logical expressions into a structured representation using the PLY (Python Lex-Yacc) library.

### Tokens

The parser recognizes the following tokens:

- `VARIABLE`: Variables in propositional logic (p, q, r, etc.)
- `NEGATION`: Negation operator (~)
- `CONJUNCTION`: Conjunction operator (and)
- `DISJUNCTION`: Disjunction operator (or)
- `IMPLICATION`: Implication operator (=>)
- `EQUALITY`: Equality operator (<=>)
- `LPAREN`, `RPAREN`: Parentheses for grouping

### Grammar Rules

The parser implements the following grammar rules:

```
formula : atom
        | conjunction
        | equality
        | negation
        | negation_with_parens
        | disjunction
        | implication

atom : VARIABLE

conjunction : LPAREN formula CONJUNCTION formula RPAREN

equality : LPAREN formula EQUALITY formula RPAREN

negation : NEGATION formula

negation_with_parens : LPAREN NEGATION formula RPAREN

implication : LPAREN formula IMPLICATION formula RPAREN

disjunction : LPAREN formula DISJUNCTION formula RPAREN
```

### Usage

To parse a logical expression:

```python
from alphabetalogic.parser import parse_formula

# Parse a logical expression
formula = parse_formula("(p and q)")

# The result is a Formula object
print(formula)  # Output: (p and q)
```

## Formula Classes

The formula module (`formula.py`) defines classes for representing logical expressions.

### Base Formula Class

The `Formula` class is the base class for all logical expressions. It provides common functionality and maintains a registry of all formula objects.

### Variable Class

The `Variable` class represents a propositional variable (e.g., p, q, r).

```python
from alphabetalogic.formula import Variable

# Create a variable
p = Variable(letter="p")
```

### Operator Classes

The library provides classes for various logical operators:

- `Conjunction`: Represents the logical AND operation
- `Disjunction`: Represents the logical OR operation
- `Implication`: Represents the logical implication (=>)
- `Equality`: Represents logical equivalence (<=>)
- `Negation`: Represents logical negation (~)

Each operator class inherits from the `Operator` base class and implements its specific behavior.

```python
from alphabetalogic.formula import Conjunction, Variable

# Create variables
p = Variable(letter="p")
q = Variable(letter="q")

# Create a conjunction
conjunction = Conjunction(arguments=[p, q])
```

### Prefix Notation

Formula objects can be converted to prefix notation using the `to_prefix_notation` method:

```python
formula = parse_formula("(p and q)")
prefix = formula.to_prefix_notation()
print(prefix)  # Output: (p and q)
```

## Tableaux Method

The tableaux module (`tableaux.py`) implements the analytical tableaux method for checking if a formula is a tautology.

The operators are expanded in following way:

      Conjunction (A ∧ B):
        ┌──────────┐
        │  A ∧ B   │
        └────┬─────┘
             │
             A
             │
             B

      Negated Conjunction ~(A ∧ B):
        ┌──────────┐
        │~(A or B) │
        └────┬─────┘
          ┌──┴──┐
          │     │
         ~A    ~B


      Disjunction (A ∨ B):
        ┌──────────┐
        │  A or B  │
        └────┬─────┘
          ┌──┴──┐
          │     │
          A     B

      Negated Disjunction ~(A ∨ B):
        ┌──────────┐
        │~(A or B) │
        └────┬─────┘
             │
            ~A
             │
            ~B

      Implication (A => B):
        ┌──────────┐
        │  A => B  │
        └────┬─────┘
          ┌──┴──┐
          │     │
         ~A     B

      Negated Implication ~(A => B):
        ┌──────────┐
        │~(A => B) │
        └────┬─────┘
             │
             A
             │
            ~B

      Equivalence (A <=> B):
        ┌──────────┐
        │  A <=> B │
        └────┬─────┘
          ┌──┴──┐
          │     │
          A    ~A
          │     │
          B    ~B

      Negated Equivalence ~(A <=> B):
        ┌──────────┐
        │~(A <=> B)│
        └────┬─────┘
          ┌──┴──┐
          │     │
          A    ~A
          │     │
         ~B     B

      Double Negation ~~A:
        ┌──────────┐
        │   ~~A    │
        └────┬─────┘
             │
             A

### Tree Class

The `Tree` class represents a tableaux tree and provides methods for growing the tree, checking for contradictions, and visualizing the tree.

### Checking Tautologies

To check if a formula is a tautology:

```python
from alphabetalogic.tableaux import check_if_tautology

# Check if a formula is a tautology
is_tautology = check_if_tautology("~(p or ~p)")
print(is_tautology)  # Output: True
```

### Visualization

The tableaux tree can be visualized using the `display` method:

```python
from alphabetalogic.tableaux import Tree, parse_pl_formula_infix_notation

# Parse a formula
formula = parse_pl_formula_infix_notation("~(p or ~p)")

# Create a tree
tree = Tree()
tree.clear([formula])
tree.grow()

# Display the tree
tree.display()
```

## API Reference

### parser.py

#### `parse_formula(formula: str) -> Formula`

Parses a logical expression into a Formula object.

- **Parameters:**
  - `formula` (str): The logical expression to parse
- **Returns:**
  - `Formula`: The parsed formula

### formula.py

#### `class Formula`

Base class for all logical expressions.

- **Methods:**
  - `get_value()`: Gets the truth value of the formula
  - `set_values(variables_dict)`: Sets the values of variables
  - `to_prefix_notation()`: Converts the formula to prefix notation

#### `class Variable(Formula)`

Represents a propositional variable.

- **Parameters:**
  - `letter` (str): The variable name (e.g., "p", "q")
- **Methods:**
  - `get_value()`: Gets the truth value of the variable
  - `set_value(value)`: Sets the truth value of the variable
  - `to_prefix_notation()`: Returns the variable name
  - `negate()`: Negates the variable

#### `class Operator(Formula)`

Base class for logical operators.

- **Parameters:**
  - `prefix` (str): The operator prefix
  - `arguments` (list): The operands
- **Methods:**
  - `to_prefix_notation()`: Converts the operator to prefix notation
  - `negate()`: Negates the operator

#### `class Conjunction(Operator)`

Represents a logical conjunction (AND).

- **Parameters:**
  - `arguments` (list): The operands
- **Methods:**
  - `get_value()`: Returns the truth value of the conjunction
  - `expand()`: Expands the conjunction in a tableaux tree

#### `class Disjunction(Operator)`

Represents a logical disjunction (OR).

- **Parameters:**
  - `arguments` (list): The operands
- **Methods:**
  - `get_value()`: Returns the truth value of the disjunction
  - `expand()`: Expands the disjunction in a tableaux tree

#### `class Implication(Operator)`

Represents a logical implication (=>).

- **Parameters:**
  - `arguments` (list): The operands
- **Methods:**
  - `get_value()`: Returns the truth value of the implication
  - `expand()`: Expands the implication in a tableaux tree

#### `class Equality(Operator)`

Represents a logical equivalence (<=>).

- **Parameters:**
  - `arguments` (list): The operands
- **Methods:**
  - `get_value()`: Returns the truth value of the equivalence
  - `expand()`: Expands the equivalence in a tableaux tree

#### `class Negation(Operator)`

Represents a logical negation (~).

- **Parameters:**
  - `arguments` (list): The operand
- **Methods:**
  - `get_value()`: Returns the truth value of the negation
  - `to_prefix_notation()`: Converts the negation to prefix notation
  - `expand()`: Expands the negation in a tableaux tree

### tableaux.py

#### `class Tree`

Represents a tableaux tree.

- **Methods:**
  - `sort(arguments)`: Sorts arguments by operator type
  - `grow()`: Grows the tree by expanding formulas
  - `clear(formula)`: Clears the structure of single and multiple negations
  - `find_leaf_nodes(edges, start_node)`: Finds leaf nodes from a start node
  - `get_end(node)`: Gets the end nodes of a branch
  - `get_branch(end_node, set_color)`: Gets the formulas in a branch
  - `display()`: Displays the tree using NetworkX and Matplotlib

#### `check_contradictions(expressions: list) -> bool`

Checks if a branch contains contradictory expressions.

- **Parameters:**
  - `expressions` (list): The expressions in the branch
- **Returns:**
  - `bool`: True if contradictions are found, False otherwise

#### `parse_pl_formula_infix_notation(text: str) -> Formula`

Parses a logical expression in infix notation.

- **Parameters:**
  - `text` (str): The logical expression to parse
- **Returns:**
  - `Formula`: The parsed formula

#### `check_if_tautology(formula: str) -> bool`

Checks if a formula is a tautology using the tableaux method.

- **Parameters:**
  - `formula` (str): The formula to check
- **Returns:**
  - `bool`: True if the formula is a tautology, False otherwise

## Usage Examples

### Basic Parsing

```python
from alphabetalogic.parser import parse_formula

# Parse a simple formula
formula = parse_formula("p")
print(formula)  # Output: p

# Parse a negation
formula = parse_formula("~p")
print(formula)  # Output: ~p

# Parse a conjunction
formula = parse_formula("(p and q)")
print(formula)  # Output: (p and q)

# Parse a disjunction
formula = parse_formula("(p or q)")
print(formula)  # Output: (p or q)

# Parse an implication
formula = parse_formula("(p => q)")
print(formula)  # Output: (p => q)

# Parse an equality
formula = parse_formula("(p <=> q)")
print(formula)  # Output: (p <=> q)

# Parse a complex formula
formula = parse_formula("((p and q) => (r or ~s))")
print(formula)  # Output: ((p and q) => (r or ~s))
```

### Checking Tautologies

```python
from alphabetalogic.tableaux import check_if_tautology

# Check if a formula is a tautology
tautologies = [
    "~(p or ~p)",  # Law of excluded middle
    "~(p <=> ~~p)",  # Double negation law
    "~(~(p and q) <=> (~p or ~q))",  # De Morgan's first law
    "~(~(p or q) <=> (~p and ~q))",  # De Morgan's second law
    "~((p and (p => q)) => q)",  # Modus ponens
]

for tautology in tautologies:
    is_tautology = check_if_tautology(tautology)
    print(f"{tautology}: {is_tautology}")
```

### Working with Formula Objects

```python
from alphabetalogic.formula import Variable, Conjunction, Disjunction, Implication, Equality, Negation

# Create variables
p = Variable(letter="p")
q = Variable(letter="q")

# Create a conjunction
conjunction = Conjunction(arguments=[p, q])
print(conjunction.to_prefix_notation())  # Output: (p and q)

# Create a disjunction
disjunction = Disjunction(arguments=[p, q])
print(disjunction.to_prefix_notation())  # Output: (p or q)

# Create an implication
implication = Implication(arguments=[p, q])
print(implication.to_prefix_notation())  # Output: (p => q)

# Create an equality
equality = Equality(arguments=[p, q])
print(equality.to_prefix_notation())  # Output: (p <=> q)

# Create a negation
negation = Negation(arguments=[p])
print(negation.to_prefix_notation())  # Output: ~p

# Set variable values
p.set_value(True)
q.set_value(False)

# Evaluate formulas
print(conjunction.get_value())  # Output: False
print(disjunction.get_value())  # Output: True
print(implication.get_value())  # Output: False
print(equality.get_value())  # Output: False
print(negation.get_value())  # Output: False
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
