"""Tests for tagless final pattern with v2 typeclass instances.

Two ways to use funstruct:
    1. Dot syntax (default): Some(10).map(f)
    2. Typeclass instance (tagless final): F.map(fa, f) where F: Monad

F is the typeclass instance — OptionMonad(), ResultMonadError(), etc.
The type hint F: Monad is the constraint (like Haskell's Functor f =>).
The caller provides F via summon(Monad, Option).
"""

import pytest

from funstruct.typeclasses import Monad, MonadError, Functor, Alternative, summon
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.result import Result, Ok, Err
from funstruct.monad.either import Either, Right, Left


class TestGenericFunctions:
    """Generic functions where F: Monad is the constraint."""

    def test_double_option(self):
        def double(F: Monad, fa):
            return F.map(fa, lambda x: x * 2)

        assert double(summon(Monad, Option), Some(21)) == Some(42)

    def test_double_result(self):
        def double(F: Monad, fa):
            return F.map(fa, lambda x: x * 2)

        assert double(summon(Monad, Result), Ok(21)) == Ok(42)

    def test_double_either(self):
        def double(F: Monad, fa):
            return F.map(fa, lambda x: x * 2)

        assert double(summon(Monad, Either), Right(21)) == Right(42)

    def test_same_function_three_effects(self):
        def increment(F: Monad, fa):
            return F.bind(fa, lambda x: F.pure(x + 1))

        assert increment(summon(Monad, Option), Some(41)) == Some(42)
        assert increment(summon(Monad, Result), Ok(41)) == Ok(42)
        assert increment(summon(Monad, Either), Right(41)) == Right(42)

    def test_short_circuit_propagates(self):
        def increment(F: Monad, fa):
            return F.bind(fa, lambda x: F.pure(x + 1))

        assert increment(summon(Monad, Option), Nothing()) == Nothing()
        assert isinstance(increment(summon(Monad, Result), Err(ValueError("x"))), Err)
        assert increment(summon(Monad, Either), Left("e")) == Left("e")


class TestMonadErrorConstraint:
    def test_safe_divide_ok(self):
        def safe_divide(F: MonadError, a, b):
            if b == 0:
                return F.raise_error(ValueError("div by zero"))
            return F.pure(a / b)

        assert safe_divide(summon(MonadError, Result), 10, 2) == Ok(5.0)

    def test_safe_divide_error(self):
        def safe_divide(F: MonadError, a, b):
            if b == 0:
                return F.raise_error(ValueError("div by zero"))
            return F.pure(a / b)

        result = safe_divide(summon(MonadError, Result), 10, 0)
        assert isinstance(result, Err)

    def test_recover_from_error(self):
        def safe_or_default(F: MonadError, fa, default):
            return F.handle_error_with(fa, lambda _: F.pure(default))

        F = summon(MonadError, Result)
        assert safe_or_default(F, Err(ValueError("x")), 0) == Ok(0)
        assert safe_or_default(F, Ok(42), 0) == Ok(42)


class TestDotSyntaxChaining:
    """Dot syntax produces the same results and chains naturally."""

    def test_chain_map_bind(self):
        result = Some(5).map(lambda x: x * 2).bind(lambda x: Some(x + 1))
        assert result == Some(11)

    def test_dot_syntax_equals_summon(self):
        f = lambda x: x + 1
        assert Some(10).map(f) == summon(Monad, Option).map(Some(10), f)
        assert Ok(10).map(f) == summon(Monad, Result).map(Ok(10), f)
        assert Right(10).map(f) == summon(Monad, Either).map(Right(10), f)

    def test_bind_dot_equals_summon(self):
        f = lambda x: Some(x + 1)
        assert Some(10).bind(f) == summon(Monad, Option).bind(Some(10), f)

    def test_operators(self):
        assert Some(1) >> (lambda x: Some(x + 1)) == Some(2)
        assert Some(1) * Some(2) == Some((1, 2))


class TestTaglessFinalWithService:
    """Full tagless final: generic program + swappable service."""

    def test_checkout_success(self):
        def checkout(F: MonadError, get_balance, amount):
            return F.bind(
                get_balance,
                lambda bal: (
                    F.raise_error(ValueError("insufficient"))
                    if bal < amount
                    else F.pure(bal - amount)
                ),
            )

        F = summon(MonadError, Result)
        assert checkout(F, Ok(500.0), 49.99) == Ok(450.01)

    def test_checkout_insufficient_funds(self):
        def checkout(F: MonadError, get_balance, amount):
            return F.bind(
                get_balance,
                lambda bal: (
                    F.raise_error(ValueError("insufficient"))
                    if bal < amount
                    else F.pure(bal - amount)
                ),
            )

        F = summon(MonadError, Result)
        result = checkout(F, Ok(5.0), 49.99)
        assert isinstance(result, Err)

    def test_checkout_user_not_found(self):
        def checkout(F: MonadError, get_balance, amount):
            return F.bind(
                get_balance,
                lambda bal: (
                    F.raise_error(ValueError("insufficient"))
                    if bal < amount
                    else F.pure(bal - amount)
                ),
            )

        F = summon(MonadError, Result)
        result = checkout(F, Err(KeyError("not found")), 49.99)
        assert isinstance(result, Err)

    def test_same_program_either(self):
        def checkout(F: MonadError, get_balance, amount):
            return F.bind(
                get_balance,
                lambda bal: (
                    F.raise_error(ValueError("insufficient"))
                    if bal < amount
                    else F.pure(bal - amount)
                ),
            )

        F = summon(MonadError, Either)
        assert checkout(F, Right(500.0), 49.99) == Right(450.01)
        assert isinstance(checkout(F, Left("err"), 49.99), Left)


class TestReturnValueChainsViaDotSyntax:
    """Return values from F.pure / F.bind can be chained with dot syntax.

    F.pure(42) returns Some(42), which has DotNotation.
    So F.pure(42).map(f) works — the generic function produces values
    that the caller can chain with dot syntax.
    """

    def test_pure_then_dot_map(self):
        F = summon(Monad, Option)
        assert F.pure(42).map(lambda x: x + 1) == Some(43)

    def test_bind_then_dot_map(self):
        F = summon(Monad, Result)
        result = F.bind(Ok(10), lambda x: F.pure(x * 2)).map(str)
        assert result == Ok("20")

    def test_generic_function_result_is_chainable(self):
        def double(F: Monad, fa):
            return F.map(fa, lambda x: x * 2)

        result = double(summon(Monad, Option), Some(5)).bind(lambda x: Some(x + 1))
        assert result == Some(11)
