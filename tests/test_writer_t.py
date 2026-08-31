"""Tests for WriterT monad transformer."""

import pytest

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.monad.either import Either, Left, Right
from funstruct.monad.option import Nothing, Option, Some
from funstruct.monadtransformer.writer_t import WriterT
from funstruct.typeclasses import Monoid, Semigroup

list_monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
clist_monoid = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())


class LogT(WriterT):
    _monoid = list_monoid


class CLogT(WriterT):
    _monoid = clist_monoid


def _writer_t_eq(a, b):
    return a.run() == b.run()


class TestPure:
    def test_pure_with_either(self):
        assert LogT.pure(42, Either).run() == Right((42, []))

    def test_pure_with_option(self):
        assert LogT.pure(42, Option).run() == Some((42, []))

    def test_pure_with_clist_monoid(self):
        assert CLogT.pure(42, Either).run() == Right((42, Nil()))


class TestTell:
    def test_tell_with_either(self):
        assert LogT.tell(["hello"], Either).run() == Right((None, ["hello"]))

    def test_tell_with_clist(self):
        w = CLogT.tell(Cons("msg", Nil()), Either)
        assert w.run() == Right((None, Cons("msg", Nil())))


class TestMap:
    def test_map_transforms_value(self):
        w = LogT(Right((5, ["init"])))
        assert w.map(lambda x: x * 2).run() == Right((10, ["init"]))

    def test_map_preserves_output(self):
        w = LogT(Right((1, ["a", "b"])))
        result = w.map(lambda x: x + 100).run()
        match result:
            case Right((val, out)):
                assert val == 101
                assert out == ["a", "b"]

    def test_map_skips_on_failure(self):
        w = LogT(Left("err"))
        assert w.map(lambda x: x * 2).run() == Left("err")

    def test_map_skips_on_nothing(self):
        w = LogT(Nothing())
        assert w.map(lambda x: x * 2).run() == Nothing()


class TestBind:
    def test_bind_accumulates_output(self):
        w = LogT(Right((1, ["start"])))
        result = w.bind(lambda x: LogT(Right((x + 1, ["inc"]))))
        assert result.run() == Right((2, ["start", "inc"]))

    def test_bind_chains_multiple(self):
        w = (
            LogT.pure(0, Either)
            .bind(lambda x: LogT(Right((x + 1, ["step1"]))))
            .bind(lambda x: LogT(Right((x + 1, ["step2"]))))
        )
        assert w.run() == Right((2, ["step1", "step2"]))

    def test_bind_short_circuits_on_left(self):
        w = LogT(Left("stop")).bind(lambda x: LogT(Right((x + 1, ["never"]))))
        assert w.run() == Left("stop")

    def test_bind_can_fail_midway(self):
        w = LogT(Right((1, ["start"]))).bind(lambda _: LogT(Left("boom")))
        assert w.run() == Left("boom")

    def test_bind_with_clist_output(self):
        w = CLogT(Right((1, Cons("a", Nil())))).bind(
            lambda x: CLogT(Right((x + 1, Cons("b", Nil()))))
        )
        assert w.run() == Right((2, CList.from_iterable(["a", "b"])))


class TestThen:
    def test_then_discards_value(self):
        w = LogT(Right(("discard", ["a"]))).then(LogT(Right(("keep", ["b"]))))
        assert w.run() == Right(("keep", ["a", "b"]))

    def test_then_short_circuits(self):
        w = LogT(Left("stop")).then(LogT(Right(("never", ["b"]))))
        assert w.run() == Left("stop")


class TestLift:
    def test_lift_wraps_with_empty_output(self):
        assert LogT.lift_f(Right(42)).run() == Right((42, []))

    def test_lift_propagates_failure(self):
        assert LogT.lift_f(Left("err")).run() == Left("err")

    def test_lift_with_option(self):
        assert LogT.lift_f(Some(5)).run() == Some((5, []))
        assert LogT.lift_f(Nothing()).run() == Nothing()


class TestOrElse:
    def test_recovers_from_failure(self):
        w = LogT(Left("oops")).or_else(
            lambda e: LogT(Right(("recovered", [f"fixed: {e}"])))
        )
        assert w.run() == Right(("recovered", ["fixed: oops"]))

    def test_skips_on_success(self):
        w = LogT(Right((42, ["ok"]))).or_else(lambda e: LogT(Right(("nope", ["bad"]))))
        assert w.run() == Right((42, ["ok"]))


class TestWithOption:
    """WriterT wrapping Option — logging + absence."""

    def test_map_some(self):
        w = LogT(Some((5, ["init"])))
        assert w.map(lambda x: x * 2).run() == Some((10, ["init"]))

    def test_bind_some(self):
        w = LogT(Some((1, ["a"]))).bind(lambda x: LogT(Some((x + 1, ["b"]))))
        assert w.run() == Some((2, ["a", "b"]))

    def test_bind_nothing(self):
        w = LogT(Nothing()).bind(lambda x: LogT(Some((x + 1, ["b"]))))
        assert w.run() == Nothing()

    def test_pure_option(self):
        assert LogT.pure(99, Option).run() == Some((99, []))


class TestLaws:
    """Monad laws for WriterT."""

    def test_left_identity(self):
        """pure(a).bind(f) == f(a)"""
        f = lambda x: LogT(Right((x + 1, ["f"])))
        left = LogT.pure(5, Either).bind(f).run()
        right = f(5).run()
        assert left == right

    def test_right_identity(self):
        """m.bind(pure) == m"""
        m = LogT(Right((42, ["init"])))
        result = m.bind(lambda a: LogT.pure(a, Either)).run()
        assert result == m.run()

    def test_associativity(self):
        """m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))"""
        m = LogT(Right((1, ["start"])))
        f = lambda x: LogT(Right((x + 1, ["f"])))
        g = lambda x: LogT(Right((x * 2, ["g"])))

        left = m.bind(f).bind(g).run()
        right = m.bind(lambda x: f(x).bind(g)).run()
        assert left == right


class TestSemigroupVsMonoid:
    """WriterT requires Monoid — Semigroup breaks pure/lift."""

    def test_semigroup_breaks_pure(self):
        int_add_sg = Semigroup(typ=int, combine=lambda a, b: a + b)

        class BadWriterT(WriterT):
            _monoid = int_add_sg

        with pytest.raises(AttributeError):
            BadWriterT.pure(42, Either)

    def test_semigroup_breaks_lift(self):
        int_add_sg = Semigroup(typ=int, combine=lambda a, b: a + b)

        class BadWriterT(WriterT):
            _monoid = int_add_sg

        with pytest.raises(AttributeError):
            BadWriterT.lift_f(Right(42))

    def test_monoid_satisfies_all(self):
        int_add = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)

        class IntLogT(WriterT):
            _monoid = int_add

        w = IntLogT.pure(42, Either).bind(lambda x: IntLogT(Right((x + 1, 5))))
        assert w.run() == Right((43, 5))


class TestDoNotation:
    """WriterT do-notation accumulates output across yields."""

    def test_do_accumulates_output(self):
        @LogT.do
        def pipeline():
            x = yield LogT(Right((1, ["start"])))
            y = yield LogT(Right((x + 10, ["step"])))
            return x + y

        assert pipeline.run() == Right((12, ["start", "step"]))

    def test_do_short_circuits_on_left(self):
        @LogT.do
        def pipeline():
            x = yield LogT(Right((1, ["ok"])))
            y = yield LogT(Left("boom"))
            return x + y

        assert pipeline.run() == Left("boom")

    def test_do_with_clist(self):
        @CLogT.do
        def pipeline():
            x = yield CLogT(Right((1, Cons("a", Nil()))))
            y = yield CLogT(Right((2, Cons("b", Nil()))))
            return x + y

        result = pipeline.run()
        assert result == Right((3, CList.from_iterable(["a", "b"])))


class TestAndThen:
    """Kleisli composition — value from self feeds into other."""

    def test_and_then_chains(self):
        step1 = LogT(Right((10, ["first"])))
        step2 = LogT(Right((99, ["second"])))
        result = step1.and_then(step2).run()
        assert result == Right((99, ["first", "second"]))

    def test_and_then_short_circuits(self):
        step1 = LogT(Left("err"))
        step2 = LogT(Right((99, ["second"])))
        result = step1.and_then(step2).run()
        assert result == Left("err")
