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
    """Applicative laws: homomorphism and ap/map2 consistency.

    1. Homomorphism — pure values combine purely:

        pure(a).ap(pure(b)) == pure((a, b))

        pure(1) ⊛ pure(2) == pure((1, 2))

    2. Consistency — ap and map2 must agree when tupling:

        fa.ap(fb) == fa.map2(fb, λa b → (a, b))

        Both produce the same paired result from two
        independent applicative values.

    These ensure that `ap` is just "combine two independent
    contexts" — no hidden sequencing or side effects.
    """
    _eq = eq or (lambda a, b: a == b)

    assert _eq(pure_fn(1).ap(pure_fn(2)), pure_fn((1, 2))), (
        "Applicative homomorphism violated: pure(1).ap(pure(2)) != pure((1,2))"
    )

    assert _eq(fa.ap(fb), fa.map2(fb, lambda a, b: (a, b))), (
        "Applicative ap/map2 consistency violated: ap must equal map2 with tupling"
    )


def assert_monad_laws(
    pure_fn: Callable[[object], Monad],
    m: Monad,
    f: Callable[[object], Monad],
    g: Callable[[object], Monad],
    eq: Eq | None = None,
) -> None:
    """Monad laws: left identity, right identity, associativity.

    1. Left identity — pure is a no-op wrapper for bind:

        pure(a).bind(f) == f(a)

        a --pure--> M[A] --bind(f)--> M[B]
        a ---------f--------------------->    (same result)

    2. Right identity — binding into pure changes nothing:

        m.bind(pure) == m

        M[A] --bind(pure)--> M[A]   (same value)

    3. Associativity — bind chains are independent of grouping:

        m.bind(f).bind(g) == m.bind(λx → f(x).bind(g))

        M[A] → M[B] → M[C]     (left-to-right)
             ≡
        M[A] → (A → M[B] → M[C])  (nested)

    These ensure that monadic pipelines behave predictably:
    pure doesn't add effects, and sequencing is associative.

    Counterexample: a monad where pure(a) adds a "tag" violates
    left identity — pure(a).bind(f) has the tag, but f(a) doesn't.
    """
    _eq = eq or (lambda a, b: a == b)

    a = 42
    assert _eq(pure_fn(a).bind(f), f(a)), (
        "Monad left identity violated: pure(a).bind(f) != f(a)"
    )

    assert _eq(m.bind(pure_fn), m), "Monad right identity violated: m.bind(pure) != m"

    assert _eq(m.bind(f).bind(g), m.bind(lambda x: f(x).bind(g))), (
        "Monad associativity violated"
    )
