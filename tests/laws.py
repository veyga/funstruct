"""
Typeclass law verification.

Call these with concrete instances to verify your type obeys the laws.

For types without structural equality (State, StateT, ReaderT),
pass an `eq` function that evaluates/runs the values for comparison.
"""

from operator import add


def assert_semigroup_laws(a, b, c, op=add):
    """Associativity: op(op(a, b), c) == op(a, op(b, c))"""
    assert op(op(a, b), c) == op(a, op(b, c)), "Semigroup associativity violated"


def assert_monoid_laws(a, empty, op=add):
    """Left/right identity: op(empty, a) == a == op(a, empty)"""
    assert op(empty, a) == a, "Monoid left identity violated"
    assert op(a, empty) == a, "Monoid right identity violated"


def assert_functor_laws(fa, eq=None):
    """Identity and composition."""
    _eq = eq or (lambda a, b: a == b)

    assert _eq(fa.map(lambda x: x), fa), "Functor identity violated"

    f = lambda x: (x, "f")
    g = lambda x: (x, "g")
    assert _eq(fa.map(f).map(g), fa.map(lambda x: g(f(x)))), (
        "Functor composition violated"
    )


def assert_applicative_laws(pure_fn, fa, fb, eq=None):
    """Applicative laws (product-style ap).

    Args:
        pure_fn: The pure function
        fa: A value F[A]
        fb: A value F[B]
        eq: Optional equality function. Defaults to ==.
    """
    _eq = eq or (lambda a, b: a == b)

    # Homomorphism: pure(a).ap(pure(b)) == pure((a, b))
    assert _eq(pure_fn(1).ap(pure_fn(2)), pure_fn((1, 2))), (
        "Applicative homomorphism violated: pure(1).ap(pure(2)) != pure((1,2))"
    )


def assert_monad_laws(pure_fn, m, f, g, eq=None):
    """Left identity, right identity, associativity.

    Args:
        pure_fn: The pure/return function
        m: A monadic value
        f: A function A -> M[B]
        g: A function B -> M[C]
        eq: Optional equality function. Defaults to ==.
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
