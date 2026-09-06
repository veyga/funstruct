"""Two ways to build a DSL: initial encoding vs tagless final.

Same arithmetic DSL, two fundamentally different approaches.

Initial (AST-based):
    Build a data tree, then walk it with interpreters.
    + Can inspect/optimize the tree before running
    + Pattern matching is natural
    - Adding a new operation requires modifying every interpreter

Final (tagless):
    Write directly against an abstract algebra. No tree.
    + Adding a new interpreter is just a new class
    + No intermediate allocation
    - Can't inspect the "program" (it's just function calls)

Usage:
    uv run python demos/14_dsl_initial_vs_final.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════════════════════
# INITIAL ENCODING (AST-based)
# ═══════════════════════════════════════════════════════════════════════

# Step 1: Define the AST — the program IS data


@dataclass(frozen=True)
class Lit:
    value: int


@dataclass(frozen=True)
class Add:
    left: object
    right: object


@dataclass(frozen=True)
class Mul:
    left: object
    right: object


@dataclass(frozen=True)
class Neg:
    expr: object


# Step 2: Build a program — it's a tree of data

initial_program = Add(Lit(1), Mul(Lit(2), Neg(Lit(3))))
#       Add
#      /   \
#    Lit    Mul
#     1    /   \
#        Lit   Neg
#         2    Lit
#               3


# Step 3: Interpreters walk the tree via pattern matching


def evaluate(expr) -> int:
    match expr:
        case Lit(n):
            return n
        case Add(a, b):
            return evaluate(a) + evaluate(b)
        case Mul(a, b):
            return evaluate(a) * evaluate(b)
        case Neg(a):
            return -evaluate(a)


def pretty_print(expr) -> str:
    match expr:
        case Lit(n):
            return str(n)
        case Add(a, b):
            return f"({pretty_print(a)} + {pretty_print(b)})"
        case Mul(a, b):
            return f"({pretty_print(a)} * {pretty_print(b)})"
        case Neg(a):
            return f"(-{pretty_print(a)})"


def count_ops(expr) -> int:
    match expr:
        case Lit(_):
            return 0
        case Add(a, b):
            return 1 + count_ops(a) + count_ops(b)
        case Mul(a, b):
            return 1 + count_ops(a) + count_ops(b)
        case Neg(a):
            return 1 + count_ops(a)


def optimize(expr):
    """Optimization pass: simplify double negation, multiply by 0/1."""
    match expr:
        case Neg(Neg(inner)):
            return optimize(inner)
        case Mul(Lit(0), _) | Mul(_, Lit(0)):
            return Lit(0)
        case Mul(Lit(1), other) | Mul(other, Lit(1)):
            return optimize(other)
        case Add(a, b):
            return Add(optimize(a), optimize(b))
        case Mul(a, b):
            return Mul(optimize(a), optimize(b))
        case Neg(a):
            return Neg(optimize(a))
        case _:
            return expr


# ═══════════════════════════════════════════════════════════════════════
# TAGLESS FINAL ENCODING (behavior-based)
# ═══════════════════════════════════════════════════════════════════════

# Step 1: Define the algebra — operations, not data


class Arith(ABC):
    @abstractmethod
    def lit(self, n: int): ...
    @abstractmethod
    def add(self, a, b): ...
    @abstractmethod
    def mul(self, a, b): ...
    @abstractmethod
    def neg(self, a): ...


# Step 2: Write the program — it's a function, not data


def final_program(E: Arith):
    return E.add(E.lit(1), E.mul(E.lit(2), E.neg(E.lit(3))))


# Step 3: Interpreters are classes implementing the algebra


class Eval(Arith):
    def lit(self, n):
        return n

    def add(self, a, b):
        return a + b

    def mul(self, a, b):
        return a * b

    def neg(self, a):
        return -a


class Pretty(Arith):
    def lit(self, n):
        return str(n)

    def add(self, a, b):
        return f"({a} + {b})"

    def mul(self, a, b):
        return f"({a} * {b})"

    def neg(self, a):
        return f"(-{a})"


class Count(Arith):
    def lit(self, n):
        return 0

    def add(self, a, b):
        return 1 + a + b

    def mul(self, a, b):
        return 1 + a + b

    def neg(self, a):
        return 1 + a


# ═══════════════════════════════════════════════════════════════════════
# Demo — same results, different trade-offs
# ═══════════════════════════════════════════════════════════════════════


def main():
    print("=== Initial encoding (AST) ===\n")
    print(f"  Program:      {initial_program}")
    print(f"  Evaluate:     {evaluate(initial_program)}")
    print(f"  PrettyPrint:  {pretty_print(initial_program)}")
    print(f"  CountOps:     {count_ops(initial_program)}")

    # Optimization — only possible with initial encoding (needs the AST)
    double_neg = Neg(Neg(Lit(42)))
    print(f"\n  Optimize --{double_neg} → {optimize(double_neg)}")
    mul_zero = Mul(Lit(0), Add(Lit(100), Lit(200)))
    print(f"  Optimize {pretty_print(mul_zero)} → {pretty_print(optimize(mul_zero))}")

    print("\n=== Tagless final encoding ===\n")
    print(f"  Evaluate:     {final_program(Eval())}")
    print(f"  PrettyPrint:  {final_program(Pretty())}")
    print(f"  CountOps:     {final_program(Count())}")

    print("\n=== Trade-offs ===\n")
    print("  Initial (AST):")
    print("    + Can inspect the tree (optimize, transform, compile)")
    print("    + Pattern matching is natural")
    print("    - Adding a new op (e.g. Div) requires updating EVERY interpreter")
    print("    - Intermediate AST allocation")
    print()
    print("  Tagless final:")
    print("    + Adding a new interpreter is just a new class")
    print("    + No intermediate AST — direct execution")
    print("    + Type-safe by construction (the algebra constrains what's expressible)")
    print("    - Can't inspect or optimize the 'program' (it's just function calls)")
    print("    - Can't serialize the program")


if __name__ == "__main__":
    main()
