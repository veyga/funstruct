"""Tests for typeclass resolution via summon.

Demonstrates:
    - Direct resolution: summon(Monad, Option) → OptionMonad instance
    - Derived resolution: summon(Functor, Option) → same instance (via Monad <: Functor)
    - Error on missing: summon(MonadError, Option) → TypeError
    - Effect-polymorphic programs using summon as TypeConstructor
"""

import pytest

from funstruct.typeclasses import (
    Alternative,
    Applicative,
    Bifunctor,
    Functor,
    Monad,
    MonadError,
    summon,
    tc_of,
)
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.either import Either, Right, Left
from funstruct.monad.result import Result, Ok, Err, AsyncResult
from funstruct.collections.cons import CList, Cons, Nil


class TestDirectResolution:
    def test_summon_monad_option(self):
        assert isinstance(summon(Monad, Option), Monad)

    def test_summon_monad_either(self):
        assert isinstance(summon(Monad, Either), Monad)

    def test_summon_monad_result(self):
        assert isinstance(summon(Monad, Result), Monad)

    def test_summon_monad_error_result(self):
        assert isinstance(summon(MonadError, Result), MonadError)

    def test_summon_monad_error_either(self):
        assert isinstance(summon(MonadError, Either), MonadError)

    def test_summon_bifunctor_either(self):
        assert isinstance(summon(Bifunctor, Either), Bifunctor)

    def test_summon_alternative_option(self):
        assert isinstance(summon(Alternative, Option), Alternative)

    def test_summon_alternative_clist(self):
        assert isinstance(summon(Alternative, CList), Alternative)


class TestDerivedResolution:
    """summon derives parent typeclasses via the inheritance hierarchy."""

    def test_functor_from_monad(self):
        assert isinstance(summon(Functor, Option), Functor)

    def test_applicative_from_monad(self):
        assert isinstance(summon(Applicative, Option), Applicative)

    def test_functor_from_monad_error(self):
        assert isinstance(summon(Functor, Result), Functor)

    def test_applicative_from_monad_error(self):
        assert isinstance(summon(Applicative, Result), Applicative)

    def test_monad_from_monad_error(self):
        assert isinstance(summon(Monad, Result), Monad)


class TestResolutionErrors:
    def test_monad_error_not_on_option(self):
        with pytest.raises(TypeError, match="No instance of MonadError for Option"):
            summon(MonadError, Option)

    def test_bifunctor_not_on_option(self):
        with pytest.raises(TypeError, match="No instance of Bifunctor for Option"):
            summon(Bifunctor, Option)

    def test_alternative_not_on_result(self):
        with pytest.raises(TypeError, match="No instance of Alternative for Result"):
            summon(Alternative, Result)


class TestTypeConstructorPattern:
    def test_pure_via_summon(self):
        F = summon(Monad, Option)
        assert F.pure(42) == Some(42)

    def test_map_via_summon(self):
        F = summon(Functor, Option)
        assert F.map(Some(10), lambda x: x * 2) == Some(20)

    def test_bind_via_summon(self):
        F = summon(Monad, Result)
        result = F.bind(Ok(10), lambda x: F.pure(x + 1))
        assert result == Ok(11)

    def test_raise_error_via_summon(self):
        F = summon(MonadError, Result)
        result = F.raise_error(ValueError("bad"))
        assert isinstance(result, Err)

    def test_empty_via_summon(self):
        F = summon(Alternative, Option)
        assert F.empty() == Nothing()


class TestEffectPolymorphicProgram:
    def test_same_program_option_and_result(self):
        def increment(F, value):
            return F.map(F.pure(value), lambda x: x + 1)

        assert increment(summon(Monad, Option), 41) == Some(42)
        assert increment(summon(Monad, Result), 41) == Ok(42)

    def test_pipeline_generic_in_f(self):
        def pipeline(F):
            return F.map(
                F.bind(F.pure(10), lambda x: F.pure(x * 2)),
                lambda x: x + 1,
            )

        assert pipeline(summon(Monad, Option)) == Some(21)
        assert pipeline(summon(Monad, Result)) == Ok(21)
        assert pipeline(summon(Monad, Either)) == Right(21)

    def test_error_handling_generic(self):
        def safe_divide(F, a, b):
            if b == 0:
                return F.raise_error(ValueError("division by zero"))
            return F.pure(a / b)

        F = summon(MonadError, Result)
        assert safe_divide(F, 10, 2) == Ok(5.0)
        assert isinstance(safe_divide(F, 10, 0), Err)

        G = summon(MonadError, Either)
        assert safe_divide(G, 10, 2) == Right(5.0)
        assert isinstance(safe_divide(G, 10, 0), Left)


class TestDotSyntaxEquivalence:
    """Dot notation == summon. Both must produce the same result."""

    def test_option_map(self):
        f = lambda x: x + 1
        assert Some(10).map(f) == summon(Monad, Option).map(Some(10), f)

    def test_option_bind(self):
        f = lambda x: Some(x + 1)
        assert Some(10).bind(f) == summon(Monad, Option).bind(Some(10), f)

    def test_result_map(self):
        f = lambda x: x * 2
        assert Ok(5).map(f) == summon(Monad, Result).map(Ok(5), f)

    def test_either_map(self):
        f = lambda x: x + 1
        assert Right(10).map(f) == summon(Monad, Either).map(Right(10), f)

    def test_rshift_operator(self):
        assert Some(1) >> (lambda x: Some(x + 1)) == Some(2)

    def test_product_operator(self):
        assert Some(1) * Some(2) == Some((1, 2))


class TestTcOf:
    """tc_of resolves the type constructor from a value — Haskell-style."""

    def test_some_resolves_to_option(self):
        assert tc_of(Some(42)) is Option

    def test_nothing_resolves_to_option(self):
        assert tc_of(Nothing()) is Option

    def test_ok_resolves_to_result(self):
        assert tc_of(Ok(1)) is Result

    def test_err_resolves_to_result(self):
        assert tc_of(Err(ValueError("x"))) is Result

    def test_right_resolves_to_either(self):
        assert tc_of(Right(1)) is Either

    def test_left_resolves_to_either(self):
        assert tc_of(Left("e")) is Either

    def test_cons_resolves_to_clist(self):
        assert tc_of(Cons(1)) is CList

    def test_unknown_type_raises(self):
        with pytest.raises(TypeError, match="No _type_constructor"):
            tc_of(42)


class TestHaskellStyleGenericFunctions:
    """Write generic functions that auto-resolve typeclasses from values.

    No @using, no given, no implicits. Just summon + tc_of.
    Same as Haskell's automatic typeclass resolution, at runtime.
    """

    def test_generic_double(self):
        def double(fa):
            F = summon(Monad, tc_of(fa))
            return F.map(fa, lambda x: x * 2)

        assert double(Some(21)) == Some(42)
        assert double(Ok(21)) == Ok(42)
        assert double(Right(21)) == Right(42)

    def test_generic_increment(self):
        def increment(fa):
            F = summon(Monad, tc_of(fa))
            return F.bind(fa, lambda x: F.pure(x + 1))

        assert increment(Some(41)) == Some(42)
        assert increment(Ok(41)) == Ok(42)

    def test_generic_safe_divide(self):
        def safe_divide(fa, b):
            F = summon(MonadError, tc_of(fa))
            return F.bind(
                fa,
                lambda a: (
                    F.raise_error(ValueError("div by zero"))
                    if b == 0
                    else F.pure(a / b)
                ),
            )

        assert safe_divide(Ok(10), 2) == Ok(5.0)
        assert isinstance(safe_divide(Ok(10), 0), Err)
        assert safe_divide(Right(10), 2) == Right(5.0)
        assert isinstance(safe_divide(Right(10), 0), Left)

    def test_generic_pipeline(self):
        def pipeline(fa):
            F = summon(Monad, tc_of(fa))
            doubled = F.bind(fa, lambda x: F.pure(x * 2))
            return F.map(doubled, lambda y: y + 1)

        assert pipeline(Some(5)) == Some(11)
        assert pipeline(Ok(5)) == Ok(11)
