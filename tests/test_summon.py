"""Tests for typeclass resolution via summon.

Demonstrates:
    - Direct resolution: summon(Monad, Option) → Option
    - Derived resolution: summon(Functor, Option) → Option (via Monad <: Functor)
    - Error on missing: summon(MonadError, Option) → TypeError
    - Effect-polymorphic programs using summon as TypeConstructor
"""

import pytest

from funstruct.typeclasses import (
    Alternative,
    Applicative,
    Bifunctor,
    Foldable,
    Functor,
    Monad,
    MonadError,
    summon,
)
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.either import Either, Right, Left
from funstruct.monad.result import Result, Ok, Err, AsyncResult
from funstruct.collections.cons import CList, Cons, Nil


class TestDirectResolution:
    def test_summon_monad_option(self):
        assert summon(Monad, Option) is Option

    def test_summon_monad_either(self):
        assert summon(Monad, Either) is Either

    def test_summon_monad_result(self):
        assert summon(Monad, Result) is Result

    def test_summon_monad_error_result(self):
        assert summon(MonadError, Result) is Result

    def test_summon_monad_error_either(self):
        assert summon(MonadError, Either) is Either

    def test_summon_bifunctor_either(self):
        assert summon(Bifunctor, Either) is Either

    def test_summon_alternative_option(self):
        assert summon(Alternative, Option) is Option

    def test_summon_alternative_clist(self):
        assert summon(Alternative, CList) is CList


class TestDerivedResolution:
    """summon derives parent typeclasses via the inheritance hierarchy.

    Option extends Monad, which extends Applicative, which extends Functor.
    So summon(Functor, Option) should resolve even though Option doesn't
    directly declare itself a Functor.
    """

    def test_functor_from_monad(self):
        assert summon(Functor, Option) is Option

    def test_applicative_from_monad(self):
        assert summon(Applicative, Option) is Option

    def test_functor_from_monad_error(self):
        assert summon(Functor, Result) is Result

    def test_applicative_from_monad_error(self):
        assert summon(Applicative, Result) is Result

    def test_monad_from_monad_error(self):
        assert summon(Monad, Result) is Result


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
    """The class itself IS the type constructor.

    F = Option means F[_] = Option. F.pure(x) = Option.pure(x) = Some(x).
    This lets you write effect-polymorphic programs.
    """

    def test_pure_via_summon(self):
        F = summon(Monad, Option)
        assert F.pure(42) == Some(42)

    def test_map_via_summon(self):
        F = summon(Functor, Option)
        assert F.pure(10).map(lambda x: x * 2) == Some(20)

    def test_bind_via_summon(self):
        F = summon(Monad, Result)
        result = F.pure(10).bind(lambda x: F.pure(x + 1))
        assert result == Ok(11)

    def test_raise_error_via_summon(self):
        F = summon(MonadError, Result)
        result = F.raise_error(ValueError("bad"))
        assert isinstance(result, Err)

    def test_empty_via_summon(self):
        F = summon(Alternative, Option)
        assert F.empty() == Nothing()


class TestEffectPolymorphicProgram:
    """Write once, run with different type constructors."""

    def test_same_program_option_and_result(self):
        def increment(F, value):
            return F.pure(value).map(lambda x: x + 1)

        assert increment(summon(Monad, Option), 41) == Some(42)
        assert increment(summon(Monad, Result), 41) == Ok(42)

    def test_pipeline_generic_in_f(self):
        def pipeline(F):
            return (
                F.pure(10)
                .bind(lambda x: F.pure(x * 2))
                .map(lambda x: x + 1)
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
