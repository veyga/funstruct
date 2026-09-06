"""Tests for trait bound enforcement via summon.

Trait bounds are enforced at runtime: summon raises TypeError with
a clear message when a type doesn't have the required typeclass instance.

These tests verify:
    - Bounds are met for registered types
    - Bounds fail for unregistered types with clear errors
    - Multiple bounds (both must be met)
    - Custom typeclasses follow the same pattern
    - Derived bounds (Monad registered → Functor resolved)
"""

import pytest

from abc import ABC, abstractmethod
from dataclasses import dataclass

from funstruct.typeclasses import (
    Alternative,
    Applicative,
    Bifunctor,
    Foldable,
    Functor,
    Monad,
    MonadError,
    summon,
    tc_of,
)
from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.either import Either, Right, Left
from funstruct.monad.result import Result, Ok, Err
from funstruct.collections.cons import CList
from funstruct.typeclasses.utils.registry import register


# ── Custom typeclasses for testing ──────────────────────────────────


class Ordering(ABC):
    @abstractmethod
    def compare(self, a, b) -> int: ...


class Printable(ABC):
    @abstractmethod
    def to_string(self, value) -> str: ...


@dataclass(frozen=True)
class Temperature:
    celsius: float


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int


class _TempOrdering(Ordering):
    def compare(self, a, b):
        return int(a.celsius - b.celsius)


class _TempPrintable(Printable):
    def to_string(self, t):
        return f"{t.celsius}°C"


register(Ordering, Temperature, _TempOrdering())
register(Printable, Temperature, _TempPrintable())


# ── Tests ────────────────────────────────────────────────────────────


class TestBoundMet:
    """Summon succeeds when the type has the required instance."""

    def test_monad_option(self):
        F = summon(Monad, Option)
        assert F.pure(42) == Some(42)

    def test_monad_error_result(self):
        F = summon(MonadError, Result)
        assert isinstance(F.raise_error(ValueError("x")), Err)

    def test_alternative_option(self):
        F = summon(Alternative, Option)
        assert F.empty() == Nothing()

    def test_custom_ordering(self):
        O = summon(Ordering, Temperature)
        assert O.compare(Temperature(100), Temperature(0)) > 0

    def test_custom_printable(self):
        P = summon(Printable, Temperature)
        assert P.to_string(Temperature(37)) == "37°C"


class TestBoundNotMet:
    """Summon raises TypeError with a clear message."""

    def test_monad_error_not_on_option(self):
        with pytest.raises(TypeError, match="No instance of MonadError for Option"):
            summon(MonadError, Option)

    def test_bifunctor_not_on_option(self):
        with pytest.raises(TypeError, match="No instance of Bifunctor for Option"):
            summon(Bifunctor, Option)

    def test_alternative_not_on_result(self):
        with pytest.raises(TypeError, match="No instance of Alternative for Result"):
            summon(Alternative, Result)

    def test_ordering_not_on_color(self):
        with pytest.raises(TypeError, match="No instance of Ordering for Color"):
            summon(Ordering, Color)

    def test_completely_unregistered_type(self):
        class Foo:
            pass

        with pytest.raises(TypeError, match="No instance of Monad for Foo"):
            summon(Monad, Foo)

    def test_unregistered_typeclass(self):
        class MyTypeclass(ABC):
            pass

        with pytest.raises(TypeError, match="No instance of MyTypeclass for Option"):
            summon(MyTypeclass, Option)


class TestDerivedBounds:
    """Registering Monad gives Functor/Applicative for free."""

    def test_functor_from_monad(self):
        F = summon(Functor, Option)
        assert F.map(Some(10), lambda x: x + 1) == Some(11)

    def test_applicative_from_monad(self):
        F = summon(Applicative, Option)
        assert F.pure(42) == Some(42)

    def test_monad_from_monad_error(self):
        F = summon(Monad, Result)
        assert F.pure(42) == Ok(42)

    def test_functor_from_monad_error(self):
        F = summon(Functor, Result)
        assert F.map(Ok(10), lambda x: x * 2) == Ok(20)


class TestMultipleBounds:
    """Functions requiring multiple bounds — both must be met."""

    def test_both_bounds_met(self):
        O = summon(Ordering, Temperature)
        P = summon(Printable, Temperature)
        temps = [Temperature(100), Temperature(0), Temperature(37)]
        import functools

        sorted_temps = sorted(temps, key=functools.cmp_to_key(O.compare))
        result = [P.to_string(t) for t in sorted_temps]
        assert result == ["0°C", "37°C", "100°C"]

    def test_one_bound_met_other_not(self):
        summon(Printable, Temperature)  # this works
        summon(Ordering, Temperature)  # this works too

        # Color has Printable but NOT Ordering
        register(
            Printable,
            Color,
            type(
                "_",
                (Printable,),
                {"to_string": lambda self, c: f"rgb({c.r},{c.g},{c.b})"},
            )(),
        )

        summon(Printable, Color)  # works
        with pytest.raises(TypeError, match="No instance of Ordering for Color"):
            summon(Ordering, Color)  # fails — Color has no Ordering


class TestTcOfForBounds:
    """tc_of resolves type constructors for auto-resolved bounds."""

    def test_some_resolves_to_option(self):
        assert tc_of(Some(42)) is Option

    def test_auto_resolve_and_use(self):
        value = Some(10)
        F = summon(Monad, tc_of(value))
        assert F.map(value, lambda x: x * 2) == Some(20)

    def test_auto_resolve_fails_for_plain_python(self):
        with pytest.raises(TypeError, match="No _type_constructor"):
            tc_of(42)

    def test_auto_resolve_fails_for_unregistered(self):
        value = Some(10)
        F_tc = tc_of(value)
        with pytest.raises(TypeError, match="No instance of MonadError for Option"):
            summon(MonadError, F_tc)
