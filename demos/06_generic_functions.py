"""Demo: generic functions with trait bounds (F: Monad).

This is the canonical way to write effect-polymorphic programs in funstruct v2.

Two ways to use the library:
    1. Dot syntax (default, like Haskell) — Some(10).map(f).bind(g)
    2. Typeclass instance (tagless final) — pass F: Monad to generic functions

The F parameter is a typeclass INSTANCE (OptionMonad, ResultMonadError),
not the type itself. The type hint `F: Monad` is the constraint — it says
"F must be a Monad." The caller provides the instance via summon.

Under the hood, this is the same mechanism as:
    Haskell:  double :: Functor f => f Int -> f Int  (compiler passes dictionary)
    Scala:    def double[F[_]: Functor](fa: F[Int])  (given/using passes instance)
    Python:   def double(F: Functor, fa): ...         (caller passes via summon)

Usage:
    uv run python -m funstruct.playground.mt11
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from funstruct.typeclasses import Monad, MonadError, summon
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.result import Result, Ok, Err
from funstruct.monad.either import Either, Right, Left


# ── Generic functions (the constraint is the type hint) ──────────────

def double(F: Monad, fa):
    """F: Monad is the constraint. Works for any Monad."""
    return F.map(fa, lambda x: x * 2)


def increment(F: Monad, fa):
    return F.bind(fa, lambda x: F.pure(x + 1))


def safe_divide(F: MonadError, a: float, b: float):
    """F: MonadError is the constraint. Works for any MonadError."""
    if b == 0:
        return F.raise_error(ValueError("division by zero"))
    return F.pure(a / b)


# ── Algebra (tagless final style) ────────────────────────────────────

@dataclass(frozen=True)
class User:
    name: str
    balance: float

class AccountService(Protocol):
    def get_user(self, name: str): ...
    def charge(self, user: User, amount: float): ...

def checkout(F: MonadError, svc: AccountService, username: str, amount: float):
    """Generic checkout — works with any MonadError effect."""
    return (
        F.bind(svc.get_user(username), lambda user:
            F.raise_error(ValueError(f"insufficient funds: {user.balance} < {amount}"))
            if user.balance < amount
            else F.bind(svc.charge(user, amount), lambda _:
                F.pure(f"charged {user.name} ${amount:.2f}")
            )
        )
    )


# ── Interpreters ─────────────────────────────────────────────────────

class ResultAccountService:
    _users = {"alice": User("Alice", 500.0), "bob": User("Bob", 5.0)}

    def get_user(self, name: str) -> Result[User]:
        if name not in self._users:
            return Err(KeyError(f"user not found: {name}"))
        return Ok(self._users[name])

    def charge(self, user: User, amount: float) -> Result[User]:
        return Ok(User(user.name, user.balance - amount))


class EitherAccountService:
    _users = {"alice": User("Alice", 500.0)}

    def get_user(self, name: str) -> Either[str, User]:
        if name not in self._users:
            return Left(f"not found: {name}")
        return Ok(self._users[name])

    def charge(self, user: User, amount: float) -> Either[str, User]:
        return Right(User(user.name, user.balance - amount))


# ── Demo ─────────────────────────────────────────────────────────────

def main():
    print("=== Generic functions (F: Monad is the constraint) ===\n")

    print("  double with Option:")
    print(f"    double(summon(Monad, Option), Some(21))  = {double(summon(Monad, Option), Some(21))}")
    print(f"    double(summon(Monad, Option), Nothing()) = {double(summon(Monad, Option), Nothing())}")

    print("\n  double with Result:")
    print(f"    double(summon(Monad, Result), Ok(21))    = {double(summon(Monad, Result), Ok(21))}")

    print("\n  Same function, three different effects:")
    for name, T in [("Option", Option), ("Result", Result), ("Either", Either)]:
        F = summon(Monad, T)
        print(f"    increment({name}): {increment(F, F.pure(41))}")

    print("\n=== MonadError constraint ===\n")

    F = summon(MonadError, Result)
    print(f"  safe_divide(10, 2) = {safe_divide(F, 10, 2)}")
    print(f"  safe_divide(10, 0) = {safe_divide(F, 10, 0)}")

    print("\n=== Tagless final — checkout service ===\n")

    F = summon(MonadError, Result)
    svc = ResultAccountService()

    print(f"  checkout alice $49.99 = {checkout(F, svc, 'alice', 49.99)}")
    print(f"  checkout bob $49.99   = {checkout(F, svc, 'bob', 49.99)}")
    print(f"  checkout nobody $1    = {checkout(F, svc, 'nobody', 1.0)}")

    print("\n=== Dot syntax vs summon — same thing ===\n")

    f = lambda x: x + 1
    dot = Some(10).map(f)
    explicit = summon(Monad, Option).map(Some(10), f)
    print(f"  Some(10).map(f)                      = {dot}")
    print(f"  summon(Monad, Option).map(Some(10), f) = {explicit}")
    print(f"  equal? {dot == explicit}")

    print("\n=== Summary ===\n")
    print("  Dot syntax:     Some(10).map(f)           — for everyday use (like Haskell)")
    print("  Typeclass inst: F.map(fa, f)              — for generic programs (tagless final)")
    print("  F: Monad        is the constraint          — the type hint IS the trait bound")
    print("  summon(Monad, Option) provides the F       — the caller resolves, once")


if __name__ == "__main__":
    main()
