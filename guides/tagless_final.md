# Tagless Final Style

## What is it?

"Programming in the tagless-final style" means writing computations
against an abstract interface (an algebra) whose concrete interpretation
is supplied later. The same program can be interpreted differently
depending on which implementation you provide.

This is a normal description in Scala FP and Haskell. It's not a
framework — it's a way of structuring programs.

## Functional programming doesn't imply tagless final

You can write very functional code without tagless final.

### Initial encoding (data-oriented FP)

Build a data representation of the program, then interpret it:

```python
# ADT representing expressions
@dataclass(frozen=True)
class Lit:
    value: int

@dataclass(frozen=True)
class Add:
    left: object
    right: object

@dataclass(frozen=True)
class Neg:
    expr: object

# The program is DATA:
program = Add(Lit(1), Neg(Lit(2)))

# Interpreters walk the data:
def evaluate(expr):
    match expr:
        case Lit(n): return n
        case Add(a, b): return evaluate(a) + evaluate(b)
        case Neg(a): return -evaluate(a)

def pretty_print(expr):
    match expr:
        case Lit(n): return str(n)
        case Add(a, b): return f"({pretty_print(a)} + {pretty_print(b)})"
        case Neg(a): return f"-({pretty_print(a)})"

evaluate(program)      # -1
pretty_print(program)  # "(1 + -(2))"
```

This is completely functional — immutable data, algebraic data types,
pattern matching, recursion. But the program is a concrete data structure
that interpreters inspect.

### Tagless final (behavior-oriented FP)

Instead of building a data tree, define an **algebra** (interface):

```python
from abc import ABC, abstractmethod

class ExprAlgebra(ABC):
    @abstractmethod
    def lit(self, n: int): ...
    @abstractmethod
    def add(self, a, b): ...
    @abstractmethod
    def neg(self, a): ...
```

Write the program against that interface — no data tree exists:

```python
def program(E: ExprAlgebra):
    return E.add(E.lit(1), E.neg(E.lit(2)))
```

The **implementation** decides what the program means:

```python
class Evaluate(ExprAlgebra):
    def lit(self, n): return n
    def add(self, a, b): return a + b
    def neg(self, a): return -a

class PrettyPrint(ExprAlgebra):
    def lit(self, n): return str(n)
    def add(self, a, b): return f"({a} + {b})"
    def neg(self, a): return f"-({a})"

program(Evaluate())      # -1
program(PrettyPrint())   # "(1 + -(2))"
```

Same program, different meanings. No AST to walk — the operations
**are** the interpretation.

## The conceptual difference

**Initial encoding:**

> First, construct a description of the computation. Later, interpret it.

```text
program → AST → interpreter → result
```

**Tagless final:**

> Write the computation directly against an abstract interface.
> The implementation provides its meaning.

```text
program → abstract algebra → chosen implementation → result
```

Or more succinctly:

- **Initial** = data representing the program
- **Final** = behavior representing the program

## Why "tagless"?

The initial representation has **tags** (constructors):

```python
case Lit(...): ...
case Add(...): ...
case Neg(...): ...
```

The interpreter must inspect those tags via pattern matching.

In tagless-final, there is **no such AST to inspect**. The operations
are represented by the algebra interface itself. No tags, no matching —
hence "tagless."

## How funstruct uses this

funstruct's typeclass system is the tagless-final pattern applied to
effect types:

```python
from funstruct.typeclasses import Monad, MonadError, summon
from funstruct.monad.option import Option, Some
from funstruct.monad.result import Result, Ok

# The "algebra" is the typeclass (Monad, MonadError, etc.)
# The "program" is generic in F:
def pipeline(F: Monad):
    return F.bind(F.pure(10), lambda x: F.pure(x + 1))

# The "implementation" is the instance, resolved via summon:
pipeline(summon(Monad, Option))  # Some(11)
pipeline(summon(Monad, Result))  # Ok(11)
```

The program doesn't know whether it's running in `Option`, `Result`,
or `Either`. The caller decides by providing the typeclass instance.

For error handling:

```python
def safe_divide(F: MonadError, a, b):
    if b == 0:
        return F.raise_error(ValueError("division by zero"))
    return F.pure(a / b)

safe_divide(summon(MonadError, Result), 10, 2)  # Ok(5.0)
safe_divide(summon(MonadError, Result), 10, 0)  # Err(ValueError(...))
```

## The two styles in funstruct

```text
Functional programming
├── Initial / data-oriented FP
│   └── ADTs + pattern matching + interpreters
│   └── funstruct provides: Option, Either, Result (the data types)
│
└── Final / tagless-final FP
    └── abstract algebras + polymorphic implementations
    └── funstruct provides: typeclasses + summon + DotNotation
```

Both styles are fully functional. Tagless final is a particular way of
structuring programs where the **effect type is abstract** — not an
alternative to functional programming itself.

## Playground demos

- `mt08.py` — tagless final intro: same program, different effects
- `mt09.py` — swapping database backends (Postgres vs in-memory vs failing)
- `mt10.py` — JSON encoder with typeclass composition and derivation
- `mt11.py` — generic functions with trait bounds (`F: Monad`)
- `mt13.py` — extending funstruct with your own types and typeclasses
