"""Embedded DSL via tagless final — no parser needed.

A DSL (Domain Specific Language) is a small language for a specific problem.
Tagless final lets you build one embedded in Python:

    1. Define the algebra (what operations exist)
    2. Write programs against the algebra
    3. Provide different interpreters (evaluate, pretty-print, optimize, compile)

The same program can be evaluated, printed, or compiled — depending on
which interpreter you provide. No AST, no parser.

This demo builds three DSLs:
    - Arithmetic expressions (eval, pretty-print, optimize)
    - A query builder (SQL generation, in-memory execution)
    - A workflow/pipeline DSL (execute, dry-run)

Usage:
    uv run python demos/13_dsl.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ═══════════════════════════════════════════════════════════════════════
# DSL 1: Arithmetic expressions
# ═══════════════════════════════════════════════════════════════════════

class Arith(ABC):
    """The algebra — defines what operations exist in the DSL."""
    @abstractmethod
    def lit(self, n: int): ...
    @abstractmethod
    def add(self, a, b): ...
    @abstractmethod
    def mul(self, a, b): ...
    @abstractmethod
    def neg(self, a): ...


def math_program(E: Arith):
    """A program written in the DSL. Doesn't know how it will be interpreted."""
    return E.add(E.lit(1), E.mul(E.lit(2), E.neg(E.lit(3))))


class Evaluate(Arith):
    """Interpreter 1: compute the result."""
    def lit(self, n): return n
    def add(self, a, b): return a + b
    def mul(self, a, b): return a * b
    def neg(self, a): return -a


class PrettyPrint(Arith):
    """Interpreter 2: produce a string representation."""
    def lit(self, n): return str(n)
    def add(self, a, b): return f"({a} + {b})"
    def mul(self, a, b): return f"({a} * {b})"
    def neg(self, a): return f"(-{a})"


class CountOps(Arith):
    """Interpreter 3: count the number of operations."""
    def lit(self, n): return 0
    def add(self, a, b): return 1 + a + b
    def mul(self, a, b): return 1 + a + b
    def neg(self, a): return 1 + a


# ═══════════════════════════════════════════════════════════════════════
# DSL 2: Query builder
# ═══════════════════════════════════════════════════════════════════════

class Query(ABC):
    """DSL for building database queries."""
    @abstractmethod
    def table(self, name: str): ...
    @abstractmethod
    def where(self, query, condition: str): ...
    @abstractmethod
    def select(self, query, *columns: str): ...
    @abstractmethod
    def limit(self, query, n: int): ...


def find_active_users(Q: Query):
    """A query program — doesn't know if it generates SQL or runs in-memory."""
    return Q.limit(
        Q.select(
            Q.where(Q.table("users"), "active = true"),
            "name", "email",
        ),
        10,
    )


class ToSQL(Query):
    """Interpreter: generate SQL string."""
    def table(self, name): return f"SELECT * FROM {name}"
    def where(self, q, cond): return f"{q} WHERE {cond}"
    def select(self, q, *cols): return q.replace("SELECT *", f"SELECT {', '.join(cols)}")
    def limit(self, q, n): return f"{q} LIMIT {n}"


class DryRun(Query):
    """Interpreter: describe what would happen."""
    def table(self, name): return [f"scan table '{name}'"]
    def where(self, q, cond): return q + [f"filter: {cond}"]
    def select(self, q, *cols): return q + [f"project: {', '.join(cols)}"]
    def limit(self, q, n): return q + [f"take first {n}"]


# ═══════════════════════════════════════════════════════════════════════
# DSL 3: Workflow / pipeline
# ═══════════════════════════════════════════════════════════════════════

class Workflow(ABC):
    """DSL for defining multi-step workflows."""
    @abstractmethod
    def step(self, name: str, fn): ...
    @abstractmethod
    def sequence(self, a, b): ...
    @abstractmethod
    def on_error(self, workflow, handler): ...


def deploy_pipeline(W: Workflow):
    """A deploy workflow — same definition, different execution."""
    return W.on_error(
        W.sequence(
            W.step("build", lambda: "artifact-v1.2"),
            W.sequence(
                W.step("test", lambda: "all passed"),
                W.step("deploy", lambda: "deployed to prod"),
            ),
        ),
        lambda err: f"ROLLBACK: {err}",
    )


class Execute(Workflow):
    """Interpreter: actually run the workflow."""
    def step(self, name, fn):
        result = fn()
        print(f"    [{name}] → {result}")
        return result
    def sequence(self, a, b): return b
    def on_error(self, workflow, handler): return workflow


class PlanOnly(Workflow):
    """Interpreter: just show the plan, don't execute."""
    def step(self, name, fn): return f"step({name})"
    def sequence(self, a, b): return f"{a} → {b}"
    def on_error(self, w, handler): return f"{w} [on_error: rollback]"


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=== DSL 1: Arithmetic expressions ===\n")
    print(f"  Program: 1 + (2 * (-3))")
    print(f"  Evaluate:     {math_program(Evaluate())}")
    print(f"  PrettyPrint:  {math_program(PrettyPrint())}")
    print(f"  CountOps:     {math_program(CountOps())} operations")

    print("\n=== DSL 2: Query builder ===\n")
    print(f"  SQL:      {find_active_users(ToSQL())}")
    print(f"  DryRun:")
    for step in find_active_users(DryRun()):
        print(f"    → {step}")

    print("\n=== DSL 3: Workflow ===\n")
    print(f"  Plan: {deploy_pipeline(PlanOnly())}")
    print(f"  Execute:")
    deploy_pipeline(Execute())

    print("\n=== The pattern ===\n")
    print("  1. Define an algebra (ABC with abstract methods)")
    print("  2. Write programs against it (functions taking the algebra)")
    print("  3. Provide interpreters (classes implementing the algebra)")
    print("  4. Same program, different meanings — no parser needed")


if __name__ == "__main__":
    main()
