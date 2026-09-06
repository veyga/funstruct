"""Tests for Option monad."""

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.monad.option import Nothing, Option, Some
from tests.laws import assert_type_contract


class TestSome:
    def test_is_some(self):
        assert Some(1).is_some is True
        assert Some(1).is_nothing is False

    def test_map(self):
        assert Some(5).map(lambda x: x * 2) == Some(10)

    def test_bind(self):
        assert Some(5).bind(lambda x: Some(x + 1)) == Some(6)

    def test_bind_to_nothing(self):
        assert Some(5).bind(lambda x: Nothing()) == Nothing()

    def test_ap_with_some(self):
        assert Some(lambda x: x + 1).ap(Some(2)) == Some(3)

    def test_ap_with_nothing(self):
        assert Some(lambda x: x + 1).ap(Nothing()) == Nothing()

    def test_product_with_some(self):
        assert Some(1).product(Some(2)) == Some((1, 2))

    def test_product_with_nothing(self):
        assert Some(1).product(Nothing()) == Nothing()

    def test_get_or_else(self):
        assert Some(42).get_or_else(0) == 42

    def test_handle_error_with(self):
        assert Some(1).handle_error_with(lambda: Some(99)) == Some(1)

    def test_filter_passes(self):
        assert Some(10).filter(lambda x: x > 5) == Some(10)

    def test_filter_fails(self):
        assert Some(3).filter(lambda x: x > 5) == Nothing()

    def test_fold(self):
        assert Some(5).fold(lambda: "nothing", lambda x: f"got {x}") == "got 5"

    def test_eq_same(self):
        assert Some(1) == Some(1)

    def test_eq_different(self):
        assert Some(1) != Some(2)

    def test_eq_with_nothing(self):
        assert Some(1) != Nothing()

    def test_eq_with_non_option(self):
        assert Some(1) != 1

    def test_bool_true(self):
        assert bool(Some(1)) is True
        assert bool(Some(0)) is True
        assert bool(Some(None)) is True


class TestNothing:
    def test_is_some(self):
        assert Nothing().is_some is False
        assert Nothing().is_nothing is True

    def test_map(self):
        assert Nothing().map(lambda x: x * 2) == Nothing()

    def test_bind(self):
        assert Nothing().bind(lambda x: Some(x + 1)) == Nothing()

    def test_ap(self):
        assert Nothing().ap(Some(1)) == Nothing()

    def test_product(self):
        assert Nothing().product(Some(1)) == Nothing()

    def test_get_or_else(self):
        assert Nothing().get_or_else(99) == 99

    def test_handle_error_with(self):
        assert Nothing().handle_error_with(lambda: Some(42)) == Some(42)

    def test_filter(self):
        assert Nothing().filter(lambda x: True) == Nothing()

    def test_fold(self):
        assert Nothing().fold(lambda: "empty", lambda x: f"got {x}") == "empty"

    def test_eq_same(self):
        assert Nothing() == Nothing()

    def test_eq_with_some(self):
        assert Nothing() != Some(1)

    def test_eq_with_non_option(self):
        assert Nothing() != "nothing"

    def test_bool_false(self):
        assert bool(Nothing()) is False

    def test_singleton(self):
        assert Nothing() is Nothing()


class TestDo:
    def test_success(self):
        def pipeline():
            x = yield Some(1)
            y = yield Some(x + 10)
            return x + y

        assert Option.do(pipeline)() == Some(12)

    def test_short_circuits(self):
        def pipeline():
            x = yield Some(1)
            y = yield Nothing()
            return x + y

        assert Option.do(pipeline)() == Nothing()

    def test_multiple_values(self):
        def pipeline():
            a = yield Some(10)
            b = yield Some(20)
            c = yield Some(30)
            return a + b + c

        assert Option.do(pipeline)() == Some(60)

    def test_with_args(self):
        def pipeline(x, y):
            a = yield Some(x)
            b = yield Some(y)
            return a + b

        assert Option.do(pipeline)(3, 7) == Some(10)

    def test_with_kwargs(self):
        def pipeline(multiplier=1):
            x = yield Some(5)
            return x * multiplier

        assert Option.do(pipeline)(multiplier=3) == Some(15)


class TestFromOptional:
    def test_some_value(self):
        assert Option.from_optional(42) == Some(42)

    def test_none_value(self):
        assert Option.from_optional(None) == Nothing()

    def test_zero_is_some(self):
        assert Option.from_optional(0) == Some(0)

    def test_empty_string_is_some(self):
        assert Option.from_optional("") == Some("")


class TestSequence:
    def test_all_some(self):
        items = Cons(Some(1), Cons(Some(2), Cons(Some(3), Nil())))
        assert Option.sequence(items) == Some(CList.from_iterable([1, 2, 3]))

    def test_with_nothing(self):
        items = Cons(Some(1), Cons(Nothing(), Cons(Some(3), Nil())))
        assert Option.sequence(items) == Nothing()

    def test_empty_list(self):
        assert Option.sequence(Nil()) == Some(Nil())


class TestTraverse:
    def test_all_succeed(self):
        values = CList.from_iterable([1, 2, 3])
        result = Option.traverse(values, lambda x: Some(x * 10))
        assert result == Some(CList.from_iterable([10, 20, 30]))

    def test_short_circuits(self):
        values = CList.from_iterable([1, 0, 3])
        result = Option.traverse(values, lambda x: Some(x) if x != 0 else Nothing())
        assert result == Nothing()


class TestPure:
    def test_pure(self):
        assert Option.pure(42) == Some(42)


class TestLaws:
    def test_type_contract(self):
        assert_type_contract(Option.pure, Some)


class TestRshift:
    def test_rshift_bind(self):
        assert (Some(1) >> (lambda x: Some(x + 10))) == Some(11)

    def test_rshift_nothing(self):
        assert (Nothing() >> (lambda x: Some(x + 10))) == Nothing()


class TestOptionInstances:
    """Tests exercising typeclass instances via summon (covers instances.py)."""

    def test_monad_pure(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Option).pure(42) == Some(42)

    def test_monad_bind_some(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Option).bind(Some(1), lambda x: Some(x + 1)) == Some(2)

    def test_monad_bind_nothing(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Option).bind(Nothing(), lambda x: Some(x + 1)) == Nothing()

    def test_monad_map_derived(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Option).map(Some(10), lambda x: x * 2) == Some(20)

    def test_monad_product_derived(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Option).product(Some(1), Some(2)) == Some((1, 2))

    def test_alternative_empty(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).empty() == Nothing()

    def test_alternative_or_else_some_returns_first(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).or_else(Some(1), Some(2)) == Some(1)

    def test_alternative_or_else_nothing_returns_fallback(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).or_else(Nothing(), Some(2)) == Some(2)

    def test_alternative_ap_some_some(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).ap(Some(lambda x: x + 1), Some(10)) == Some(11)

    def test_alternative_ap_nothing_some(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).ap(Nothing(), Some(10)) == Nothing()

    def test_alternative_ap_some_nothing(self):
        from funstruct.typeclasses import Alternative, summon
        assert summon(Alternative, Option).ap(Some(lambda x: x + 1), Nothing()) == Nothing()

    def test_dot_vs_summon_map(self):
        from funstruct.typeclasses import Monad, summon
        f = lambda x: x + 1
        assert Some(10).map(f) == summon(Monad, Option).map(Some(10), f)

    def test_dot_vs_summon_bind(self):
        from funstruct.typeclasses import Monad, summon
        f = lambda x: Some(x + 1)
        assert Some(10).bind(f) == summon(Monad, Option).bind(Some(10), f)

    def test_dot_vs_summon_or_else(self):
        from funstruct.typeclasses import Alternative, summon
        assert Nothing().or_else(Some(5)) == summon(Alternative, Option).or_else(Nothing(), Some(5))
