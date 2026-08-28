"""
Typeclass law verification.

Call these with concrete instances to verify your type obeys the laws.

For types without structural equality (State, StateT, ReaderT),
pass an `eq` function that evaluates/runs the values for comparison.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses import (
    Applicative,
    Functor,
    Monad,
    Monoid,
    Semigroup,
)

A = TypeVar("A")
Eq = Callable[[object, object], bool]


def assert_semigroup_laws(a: A, b: A, c: A, sg: Semigroup) -> None:
    """Associativity: sg.combine(sg.combine(a, b), c) == sg.combine(a, sg.combine(b, c))"""
    left = sg.combine(sg.combine(a, b), c)
    right = sg.combine(a, sg.combine(b, c))
    assert left == right, "Semigroup associativity violated"


def assert_monoid_laws(a: A, sg: Monoid) -> None:
    """Left/right identity: combine(empty, a) == a == combine(a, empty)"""
    assert sg.combine(sg.empty, a) == a, "Monoid left identity violated"
    assert sg.combine(a, sg.empty) == a, "Monoid right identity violated"


def assert_functor_laws(fa: Functor, eq: Eq | None = None) -> None:
    """Identity and composition."""
    _eq = eq or (lambda a, b: a == b)

    assert _eq(fa.map(lambda x: x), fa), "Functor identity violated"

    f = lambda x: (x, "f")
    g = lambda x: (x, "g")
    assert _eq(fa.map(f).map(g), fa.map(lambda x: g(f(x)))), (
        "Functor composition violated"
    )


def assert_applicative_laws(
    pure_fn: Callable[[object], Applicative],
    fa: Applicative,
    fb: Applicative,
    eq: Eq | None = None,
) -> None:
    """Applicative homomorphism: pure(a).ap(pure(b)) == pure((a, b))"""
    _eq = eq or (lambda a, b: a == b)

    assert _eq(pure_fn(1).ap(pure_fn(2)), pure_fn((1, 2))), (
        "Applicative homomorphism violated: pure(1).ap(pure(2)) != pure((1,2))"
    )


def assert_monad_laws(
    pure_fn: Callable[[object], Monad],
    m: Monad,
    f: Callable[[object], Monad],
    g: Callable[[object], Monad],
    eq: Eq | None = None,
) -> None:
    """Left identity, right identity, associativity."""
    _eq = eq or (lambda a, b: a == b)

    a = 42
    assert _eq(pure_fn(a).bind(f), f(a)), (
        "Monad left identity violated: pure(a).bind(f) != f(a)"
    )

    assert _eq(m.bind(pure_fn), m), (
        "Monad right identity violated: m.bind(pure) != m"
    )

    assert _eq(m.bind(f).bind(g), m.bind(lambda x: f(x).bind(g))), (
        "Monad associativity violated"
    )
