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


def assert_type_contract(
    pure_fn: Callable,
    success_type: type,
    is_monad: bool = True,
) -> None:
    """Verify a concrete type implements the required typeclass contract.

    Every type extending Applicative must have a pure that returns the
    correct success type. The derived map and ap must also preserve it.

    For Monads, bind must also preserve the type.
    """
    val = pure_fn(1)
    assert type(val) is success_type, (
        f"pure must return {success_type.__name__}, got {type(val).__name__}"
    )

    mapped = pure_fn(1).map(lambda x: x + 1)
    assert type(mapped) is success_type, (
        f"map must return {success_type.__name__}, got {type(mapped).__name__}"
    )

    ap_result = pure_fn(lambda x: x).ap(pure_fn(1))
    assert type(ap_result) is success_type, (
        f"ap must return {success_type.__name__}, got {type(ap_result).__name__}"
    )

    if is_monad:
        bound = pure_fn(1).bind(pure_fn)
        assert type(bound) is success_type, (
            f"bind must return {success_type.__name__}, got {type(bound).__name__}"
        )


def assert_semigroup_laws(a: A, b: A, c: A, sg: Semigroup) -> None:
    """Semigroup law: associativity.

    A binary operation ⊕ is associative if grouping doesn't matter:

        (a ⊕ b) ⊕ c  ==  a ⊕ (b ⊕ c)

    Diagram:

        combine(combine(a, b), c)
              ⊕                       ==  combine(a, combine(b, c))
             / \\                                   ⊕
            ⊕   c                                 / \\
           / \\                                   a   ⊕
          a   b                                     / \\
                                                   b   c

    Counterexample: subtraction is NOT associative:
        (10 - 3) - 1 = 6  !=  10 - (3 - 1) = 8
    """
    left = sg.combine(sg.combine(a, b), c)
    right = sg.combine(a, sg.combine(b, c))
    assert left == right, "Semigroup associativity violated"


def assert_monoid_laws(a: A, sg: Monoid) -> None:
    """Monoid laws: left and right identity.

    A monoid extends semigroup with an identity element `empty` such that:

        combine(empty, a) == a    (left identity)
        combine(a, empty) == a    (right identity)

    Diagram:

        empty ⊕ a == a      a ⊕ empty == a
          ⊕                    ⊕
         / \\                  / \\
        ε   a  →  a          a   ε  →  a

    Counterexample: Monoid(int, +, empty=1) violates identity:
        combine(1, 5) = 6 != 5
    """
    assert sg.combine(sg.empty, a) == a, "Monoid left identity violated"
    assert sg.combine(a, sg.empty) == a, "Monoid right identity violated"


def assert_functor_laws(fa: Functor, eq: Eq | None = None) -> None:
    """Functor laws: identity and composition.

    1. Identity — mapping the identity function changes nothing:

        fa.map(id) == fa

        F[A] --map(x→x)--> F[A]   (same value)

    2. Composition — mapping f then g equals mapping their composition:

        fa.map(f).map(g) == fa.map(g ∘ f)

        F[A] --map(f)--> F[B] --map(g)--> F[C]
          \\                                 /
           \\------map(x → g(f(x)))--------/

    Counterexample: a box that increments a counter on every map
    violates identity — map(id) changes the counter.
    """
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
    """Applicative laws: homomorphism, product/map2 consistency, type preservation.

    1. Homomorphism — pure(f).ap(pure(a)) == pure(f(a))
    2. Consistency — fa.product(fb) == fa.map2(fb, λa b → (a, b))
    3. Type preservation — pure, map, ap all return the expected type
    """
    _eq = eq or (lambda a, b: a == b)
    success_type = type(pure_fn(1))

    f = lambda x: (x, "tagged")
    assert _eq(pure_fn(f).ap(pure_fn(1)), pure_fn(f(1))), (
        "Applicative homomorphism violated: pure(f).ap(pure(a)) != pure(f(a))"
    )

    assert _eq(fa.product(fb), fa.map2(fb, lambda a, b: (a, b))), (
        "Applicative product/map2 consistency violated"
    )

    assert type(pure_fn(1)) is success_type, (
        f"Type preservation: pure must return {success_type.__name__}, "
        f"got {type(pure_fn(1)).__name__}"
    )
    mapped = pure_fn(1).map(lambda x: x)
    assert type(mapped) is success_type, (
        f"Type preservation: map must return {success_type.__name__}, "
        f"got {type(mapped).__name__}"
    )
    ap_result = pure_fn(lambda x: x).ap(pure_fn(1))
    assert type(ap_result) is success_type, (
        f"Type preservation: ap must return {success_type.__name__}, "
        f"got {type(ap_result).__name__}"
    )


def assert_monad_laws(
    pure_fn: Callable[[object], Monad],
    m: Monad,
    f: Callable[[object], Monad],
    g: Callable[[object], Monad],
    eq: Eq | None = None,
) -> None:
    """Monad laws: left identity, right identity, associativity, type preservation.

    1. Left identity — pure(a).bind(f) == f(a)
    2. Right identity — m.bind(pure) == m
    3. Associativity — m.bind(f).bind(g) == m.bind(λx → f(x).bind(g))
    4. Type preservation — pure, map, bind, ap all return the expected type
    """
    _eq = eq or (lambda a, b: a == b)
    success_type = type(pure_fn(1))

    a = 42
    assert _eq(pure_fn(a).bind(f), f(a)), (
        "Monad left identity violated: pure(a).bind(f) != f(a)"
    )

    assert _eq(m.bind(pure_fn), m), "Monad right identity violated: m.bind(pure) != m"

    assert _eq(m.bind(f).bind(g), m.bind(lambda x: f(x).bind(g))), (
        "Monad associativity violated"
    )

    assert type(pure_fn(1)) is success_type, (
        f"Type preservation: pure must return {success_type.__name__}, "
        f"got {type(pure_fn(1)).__name__}"
    )
    mapped = pure_fn(1).map(lambda x: x)
    assert type(mapped) is success_type, (
        f"Type preservation: map must return {success_type.__name__}, "
        f"got {type(mapped).__name__}"
    )
    bound = pure_fn(1).bind(pure_fn)
    assert type(bound) is success_type, (
        f"Type preservation: bind must return {success_type.__name__}, "
        f"got {type(bound).__name__}"
    )
    ap_result = pure_fn(lambda x: x).ap(pure_fn(1))
    assert type(ap_result) is success_type, (
        f"Type preservation: ap must return {success_type.__name__}, "
        f"got {type(ap_result).__name__}"
    )
