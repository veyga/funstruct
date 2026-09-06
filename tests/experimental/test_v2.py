"""Tests for v2 prototype — separated data + typeclass instances + summon.

Demonstrates the Scala-style architecture:
    Data types are plain (no typeclass methods on Some/Nothing/Ok/Err)
    Typeclass operations come from instance classes via summon
    Derived operations (map, ap) come from the typeclass hierarchy
"""

import pytest

# Import instances to trigger registration
import funstruct.experimental.v2.option_instances  # noqa: F401
import funstruct.experimental.v2.result_instances  # noqa: F401
import funstruct.experimental.v2.clist_instances  # noqa: F401

from funstruct.experimental.v2._registry import summon
from funstruct.experimental.v2._typeclasses import (
    Alternative,
    Applicative,
    Functor,
    Monad,
    MonadError,
    Traversable,
)
from funstruct.experimental.v2.option import Nothing, Option, Some
from funstruct.experimental.v2.result import Err, Ok, Result
from funstruct.experimental.v2.clist import CList, Cons, Nil, from_list


# ── Direct resolution ────────────────────────────────────────────────


class TestDirectResolution:
    def test_summon_monad_option(self):
        m = summon(Monad, Option)
        assert isinstance(m, Monad)

    def test_summon_monad_error_result(self):
        m = summon(MonadError, Result)
        assert isinstance(m, MonadError)

    def test_summon_alternative_option(self):
        a = summon(Alternative, Option)
        assert isinstance(a, Alternative)


# ── Derived resolution ───────────────────────────────────────────────


class TestDerivedResolution:
    """Monad registered → Functor/Applicative derived automatically."""

    def test_functor_from_monad(self):
        f = summon(Functor, Option)
        assert isinstance(f, Functor)

    def test_applicative_from_monad(self):
        a = summon(Applicative, Option)
        assert isinstance(a, Applicative)

    def test_functor_from_monad_error(self):
        f = summon(Functor, Result)
        assert isinstance(f, Functor)

    def test_monad_from_monad_error(self):
        m = summon(Monad, Result)
        assert isinstance(m, Monad)


class TestResolutionErrors:
    def test_monad_error_not_on_option(self):
        with pytest.raises(TypeError, match="No instance of MonadError for Option"):
            summon(MonadError, Option)


# ── Primitives (implemented by instance) ─────────────────────────────


class TestPrimitives:
    def test_pure(self):
        F = summon(Monad, Option)
        assert F.pure(42) == Some(42)

    def test_bind_some(self):
        F = summon(Monad, Option)
        assert F.bind(Some(1), lambda x: F.pure(x + 1)) == Some(2)

    def test_bind_nothing(self):
        F = summon(Monad, Option)
        assert F.bind(Nothing(), lambda x: F.pure(x + 1)) == Nothing()


# ── Derived operations (inherited from hierarchy, NOT implemented) ───


class TestDerivedOperations:
    """These are the payoff: map, ap, map2, product come for FREE.

    OptionMonad only implements pure + bind.
    Everything below is derived from the Monad hierarchy.
    """

    def test_map_derived_from_bind_pure(self):
        F = summon(Functor, Option)
        assert F.map(Some(10), lambda x: x * 2) == Some(20)

    def test_map_nothing(self):
        F = summon(Functor, Option)
        assert F.map(Nothing(), lambda x: x * 2) == Nothing()

    def test_ap_derived_from_bind_map(self):
        F = summon(Applicative, Option)
        assert F.ap(Some(lambda x: x + 1), Some(10)) == Some(11)

    def test_ap_nothing_function(self):
        F = summon(Applicative, Option)
        assert F.ap(Nothing(), Some(10)) == Nothing()

    def test_product_derived(self):
        F = summon(Applicative, Option)
        assert F.product(Some(1), Some(2)) == Some((1, 2))

    def test_product_nothing(self):
        F = summon(Applicative, Option)
        assert F.product(Some(1), Nothing()) == Nothing()

    def test_map2_derived(self):
        F = summon(Applicative, Option)
        assert F.map2(Some(1), Some(2), lambda a, b: a + b) == Some(3)


# ── MonadError on Result ─────────────────────────────────────────────


class TestResultMonadError:
    def test_pure(self):
        F = summon(Monad, Result)
        assert F.pure(42) == Ok(42)

    def test_bind_ok(self):
        F = summon(Monad, Result)
        assert F.bind(Ok(1), lambda x: F.pure(x + 1)) == Ok(2)

    def test_bind_err(self):
        F = summon(Monad, Result)
        err = Err(ValueError("bad"))
        assert F.bind(err, lambda x: F.pure(x + 1)) == err

    def test_map_derived(self):
        F = summon(Functor, Result)
        assert F.map(Ok(10), lambda x: x * 2) == Ok(20)

    def test_raise_error(self):
        F = summon(MonadError, Result)
        result = F.raise_error(ValueError("oops"))
        assert isinstance(result, Err)

    def test_handle_error_with(self):
        F = summon(MonadError, Result)
        recovered = F.handle_error_with(
            Err(ValueError("bad")),
            lambda e: Ok("recovered"),
        )
        assert recovered == Ok("recovered")

    def test_handle_error_with_ok_passthrough(self):
        F = summon(MonadError, Result)
        assert F.handle_error_with(Ok(42), lambda e: Ok(0)) == Ok(42)


# ── Alternative on Option ────────────────────────────────────────────


class TestOptionAlternative:
    def test_empty(self):
        F = summon(Alternative, Option)
        assert F.empty() == Nothing()

    def test_or_else_some(self):
        F = summon(Alternative, Option)
        assert F.or_else(Some(1), Some(2)) == Some(1)

    def test_or_else_nothing(self):
        F = summon(Alternative, Option)
        assert F.or_else(Nothing(), Some(2)) == Some(2)


# ── Effect-polymorphic programs ──────────────────────────────────────


class TestEffectPolymorphic:
    """Write once, swap the effect via summon. This is the whole point."""

    def test_same_pipeline_different_effects(self):
        def pipeline(F):
            return F.bind(
                F.pure(10),
                lambda x: F.map(F.pure(x * 2), lambda y: y + 1),
            )

        assert pipeline(summon(Monad, Option)) == Some(21)
        assert pipeline(summon(Monad, Result)) == Ok(21)

    def test_generic_safe_divide(self):
        def safe_divide(F, a, b):
            if b == 0:
                return F.raise_error(ValueError("division by zero"))
            return F.pure(a / b)

        F = summon(MonadError, Result)
        assert safe_divide(F, 10, 2) == Ok(5.0)
        assert isinstance(safe_divide(F, 10, 0), Err)

    def test_chained_operations(self):
        def program(F):
            result = F.pure(5)
            result = F.map(result, lambda x: x * 2)       # 10
            result = F.bind(result, lambda x: F.pure(x + 1))  # 11
            result = F.map(result, str)                    # "11"
            return result

        assert program(summon(Monad, Option)) == Some("11")
        assert program(summon(Monad, Result)) == Ok("11")


# ── Dot syntax (like Scala's import cats.syntax.all._) ───────────────


class TestDotSyntax:
    """Both styles work on the same types.

    Dot syntax:       Some(10).map(f)
    Explicit summon:  summon(Functor, Option).map(Some(10), f)

    Dot syntax delegates to summon internally, just like Scala's
    extension methods desugar to typeclass instance calls.
    """

    def test_map_dot_syntax(self):
        assert Some(10).map(lambda x: x * 2) == Some(20)

    def test_map_nothing_dot_syntax(self):
        assert Nothing().map(lambda x: x * 2) == Nothing()

    def test_bind_dot_syntax(self):
        assert Some(1).bind(lambda x: Some(x + 1)) == Some(2)

    def test_bind_nothing_dot_syntax(self):
        assert Nothing().bind(lambda x: Some(x + 1)) == Nothing()

    def test_result_map_dot_syntax(self):
        assert Ok(10).map(lambda x: x * 2) == Ok(20)

    def test_result_bind_dot_syntax(self):
        assert Ok(1).bind(lambda x: Ok(x + 1)) == Ok(2)

    def test_err_map_dot_syntax(self):
        err = Err(ValueError("bad"))
        assert err.map(lambda x: x * 2) == err

    def test_err_bind_dot_syntax(self):
        err = Err(ValueError("bad"))
        assert err.bind(lambda x: Ok(x + 1)) == err

    def test_handle_error_with_dot_syntax(self):
        result = Err(ValueError("bad")).handle_error_with(lambda e: Ok("recovered"))
        assert result == Ok("recovered")

    def test_chained_dot_syntax(self):
        result = (
            Some(5)
            .map(lambda x: x * 2)
            .bind(lambda x: Some(x + 1))
            .map(str)
        )
        assert result == Some("11")

    def test_dot_and_summon_produce_same_result(self):
        f = lambda x: x + 1
        dot_result = Some(10).map(f)
        summon_result = summon(Functor, Option).map(Some(10), f)
        assert dot_result == summon_result


# ── Traversable ──────────────────────────────────────────────────────


class TestTraversable:
    """Traversable takes an Applicative instance G for the target effect.

    This is cleaner than v1's pure_fn parameter — you just pass the
    Applicative instance (or summon it).
    """

    def test_traverse_clist_with_option(self):
        """CList[A] → (A → Option[B]) → Option[CList[B]]"""
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = from_list([1, 2, 3])
        result = T.traverse(xs, lambda x: Some(x * 10), G)
        assert result == Some(from_list([10, 20, 30]))

    def test_traverse_short_circuits_on_nothing(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = from_list([1, 0, 3])
        result = T.traverse(xs, lambda x: Some(x) if x != 0 else Nothing(), G)
        assert result == Nothing()

    def test_sequence_clist_of_options(self):
        """CList[Option[A]] → Option[CList[A]]"""
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = from_list([Some(1), Some(2), Some(3)])
        result = T.sequence(xs, G)
        assert result == Some(from_list([1, 2, 3]))

    def test_sequence_short_circuits(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = from_list([Some(1), Nothing(), Some(3)])
        result = T.sequence(xs, G)
        assert result == Nothing()

    def test_traverse_empty_list(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        result = T.traverse(Nil(), lambda x: Some(x), G)
        assert result == Some(Nil())

    def test_fold_left(self):
        T = summon(Traversable, CList)
        xs = from_list([1, 2, 3])
        assert T.fold_left(xs, 0, lambda acc, x: acc + x) == 6

    def test_fold_right(self):
        T = summon(Traversable, CList)
        xs = from_list([1, 2, 3])
        result = T.fold_right(xs, [], lambda x, acc: [x] + acc)
        assert result == [1, 2, 3]

    def test_traverse_with_result(self):
        """CList[A] → (A → Result[B]) → Result[CList[B]]"""
        T = summon(Traversable, CList)
        G = summon(Applicative, Result)
        xs = from_list([1, 2, 3])
        result = T.traverse(xs, lambda x: Ok(x * 10), G)
        assert result == Ok(from_list([10, 20, 30]))


class TestCListMonad:
    def test_pure(self):
        F = summon(Monad, CList)
        assert F.pure(42) == Cons(42)

    def test_map(self):
        F = summon(Functor, CList)
        xs = from_list([1, 2, 3])
        result = F.map(xs, lambda x: x * 10)
        assert result == from_list([10, 20, 30])

    def test_bind(self):
        F = summon(Monad, CList)
        xs = from_list([1, 2, 3])
        result = F.bind(xs, lambda x: from_list([x, x]))
        assert result == from_list([1, 1, 2, 2, 3, 3])

    def test_dot_syntax_map(self):
        xs = from_list([1, 2, 3])
        assert xs.map(lambda x: x * 2) == from_list([2, 4, 6])
