"""Demo: generic functions with trait bounds (M: Monad[F]).

Write a function once, use it with any effect type. The M parameter is a
typeclass instance — the caller provides it via summon.

Under the hood, this is the same mechanism as:
    Haskell:  double :: Functor f => f Int -> f Int   (compiler passes dictionary)
    Scala:    def double[F[_]: Functor](fa: F[Int])   (implicit Functor[F] instance)
    Python:   def double(M: Monad[F], fa: F) -> F     (caller passes via summon)

For the tagless final pattern (algebras + swappable interpreters), see:
    demos/03_tagless_final_intro.py
    demos/04_tagless_final_db.py

Run: uv run python demos/05_generic_functions.py
"""

from __future__ import annotations

from demos._util import header
from funstruct.typeclasses import Monad, MonadError, summon
from funstruct.types.either import Either, Right
from funstruct.types.option import Nothing, Option, Some
from funstruct.types.result import Ok, Result

# ── Generic functions (the constraint is the type hint) ──────────────


def double[F](M: Monad[F], fa: F) -> F:
    return M.map(fa, lambda x: x * 2)


def increment[F](M: Monad[F], fa: F) -> F:
    return M.bind(fa, lambda x: M.pure(x + 1))


def safe_divide[F](M: MonadError[F], a: float, b: float) -> F:
    if b == 0:
        return M.raise_error(ValueError("division by zero"))
    return M.pure(a / b)


# ── Demo ─────────────────────────────────────────────────────────────


def main():
    header("One function, many effects")

    print("  double with Option:")
    M = summon(Monad, Option)
    print(f"    double(M, Some(21))  = {double(M, Some(21))}")
    print(f"    double(M, Nothing()) = {double(M, Nothing())}")

    print("\n  double with Result:")
    M = summon(Monad, Result)
    print(f"    double(M, Ok(21))    = {double(M, Ok(21))}")

    print("\n  double with Either:")
    M = summon(Monad, Either)
    print(f"    double(M, Right(21)) = {double(M, Right(21))}")

    header("Same function, three effects")

    for name, T in [("Option", Option), ("Result", Result), ("Either", Either)]:
        M = summon(Monad, T)
        print(f"  increment({name}): {increment(M, M.pure(41))}")

    header("MonadError constraint")

    M = summon(MonadError, Result)
    print(f"  safe_divide(10, 2) = {safe_divide(M, 10, 2)}")
    print(f"  safe_divide(10, 0) = {safe_divide(M, 10, 0)}")

    header("Dot syntax vs summon — same thing")

    f = lambda x: x + 1
    dot = Some(10).map(f)
    explicit = summon(Monad, Option).map(Some(10), f)
    print(f"  Some(10).map(f)                        = {dot}")
    print(f"  summon(Monad, Option).map(Some(10), f)  = {explicit}")
    print(f"  equal? {dot == explicit}")


if __name__ == "__main__":
    main()
