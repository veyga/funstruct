"""Benchmarks for typeclass dispatch overhead.

Measures the cost of:
    - DotNotation dispatch (Some(10).map(f) vs direct call)
    - summon resolution time
    - do-notation vs raw bind chains
    - Monad law operations (pure → bind → map)
"""

from funstruct.monad.option import Option, Some, Nothing
from funstruct.monad.result import Result, Ok, Err, AsyncResult
from funstruct.monad.either import Either, Right, Left
from funstruct.collections.cons import CList, Cons, Nil
from funstruct.typeclasses import Alternative, Functor, Monad, MonadError, summon, tc_of


class TestDotNotationOverhead:
    """Measure the cost of __getattr__ dispatch via DotNotation."""

    def test_dot_map_option(self, benchmark):
        """Some(10).map(f) — goes through DotNotation.__getattr__ → summon."""
        v = Some(10)
        benchmark(lambda: v.map(lambda x: x + 1))

    def test_dot_bind_option(self, benchmark):
        v = Some(10)
        benchmark(lambda: v.bind(lambda x: Some(x + 1)))

    def test_dot_map_result(self, benchmark):
        v = Ok(10)
        benchmark(lambda: v.map(lambda x: x + 1))

    def test_dot_bind_result(self, benchmark):
        v = Ok(10)
        benchmark(lambda: v.bind(lambda x: Ok(x + 1)))

    def test_dot_map_either(self, benchmark):
        v = Right(10)
        benchmark(lambda: v.map(lambda x: x + 1))

    def test_dot_chain_3_maps(self, benchmark):
        """Chain 3 maps — each goes through DotNotation dispatch."""
        v = Some(10)
        benchmark(lambda: v.map(lambda x: x + 1).map(lambda x: x * 2).map(str))

    def test_dot_chain_bind_map(self, benchmark):
        v = Some(5)
        benchmark(lambda: v.bind(lambda x: Some(x * 2)).map(lambda x: x + 1))


class TestSummonResolution:
    """Measure summon lookup time."""

    def test_summon_monad_option(self, benchmark):
        benchmark(lambda: summon(Monad, Option))

    def test_summon_functor_option_derived(self, benchmark):
        """Functor for Option derived from Monad — tests hierarchy walk."""
        benchmark(lambda: summon(Functor, Option))

    def test_summon_monad_error_result(self, benchmark):
        benchmark(lambda: summon(MonadError, Result))

    def test_summon_alternative_option(self, benchmark):
        benchmark(lambda: summon(Alternative, Option))

    def test_tc_of_some(self, benchmark):
        """tc_of resolves type constructor from a value."""
        v = Some(42)
        benchmark(lambda: tc_of(v))

    def test_tc_of_ok(self, benchmark):
        v = Ok(42)
        benchmark(lambda: tc_of(v))


class TestSummonVsDotNotation:
    """Compare explicit summon vs dot notation dispatch."""

    def test_explicit_summon_map(self, benchmark):
        """summon(Monad, Option).map(v, f) — pre-resolved instance."""
        F = summon(Monad, Option)
        v = Some(10)
        benchmark(lambda: F.map(v, lambda x: x + 1))

    def test_dot_notation_map(self, benchmark):
        """v.map(f) — DotNotation resolves via __getattr__ each time."""
        v = Some(10)
        benchmark(lambda: v.map(lambda x: x + 1))


class TestDoNotationOverhead:
    """Compare do-notation vs raw bind chains."""

    def test_do_notation_3_steps(self, benchmark):
        @Result.do
        def pipeline():
            x = yield Ok(10)
            y = yield Ok(x + 1)
            z = yield Ok(y * 2)
            return z
        benchmark(pipeline)

    def test_bind_chain_3_steps(self, benchmark):
        def pipeline():
            return (
                Ok(10)
                .bind(lambda x: Ok(x + 1))
                .bind(lambda y: Ok(y * 2))
            )
        benchmark(pipeline)

    def test_do_notation_5_steps(self, benchmark):
        @Result.do
        def pipeline():
            a = yield Ok(1)
            b = yield Ok(a + 1)
            c = yield Ok(b + 1)
            d = yield Ok(c + 1)
            e = yield Ok(d + 1)
            return e
        benchmark(pipeline)

    def test_bind_chain_5_steps(self, benchmark):
        def pipeline():
            return (
                Ok(1)
                .bind(lambda a: Ok(a + 1))
                .bind(lambda b: Ok(b + 1))
                .bind(lambda c: Ok(c + 1))
                .bind(lambda d: Ok(d + 1))
            )
        benchmark(pipeline)

    def test_do_short_circuit(self, benchmark):
        """do-notation that short-circuits on first Err."""
        @Result.do
        def pipeline():
            x = yield Err(ValueError("stop"))
            y = yield Ok(x + 1)
            return y
        benchmark(pipeline)

    def test_bind_short_circuit(self, benchmark):
        def pipeline():
            return Err(ValueError("stop")).bind(lambda x: Ok(x + 1))
        benchmark(pipeline)


class TestMonadLawOperations:
    """Benchmark the fundamental monad operations."""

    def test_pure_option(self, benchmark):
        benchmark(lambda: Option.pure(42))

    def test_pure_result(self, benchmark):
        benchmark(lambda: Result.pure(42))

    def test_pure_via_summon(self, benchmark):
        F = summon(Monad, Option)
        benchmark(lambda: F.pure(42))

    def test_map_derived_from_bind(self, benchmark):
        """Monad.map is derived from bind + pure. Measure overhead."""
        F = summon(Monad, Option)
        v = Some(10)
        benchmark(lambda: F.map(v, lambda x: x + 1))

    def test_ap_derived_from_bind_map(self, benchmark):
        """Monad.ap is derived from bind + map."""
        F = summon(Monad, Option)
        ff = Some(lambda x: x + 1)
        fa = Some(10)
        benchmark(lambda: F.ap(ff, fa))

    def test_product_derived(self, benchmark):
        F = summon(Monad, Option)
        a = Some(1)
        b = Some(2)
        benchmark(lambda: F.product(a, b))


class TestNothingErrShortCircuit:
    """Benchmark short-circuit paths — should be very fast."""

    def test_nothing_map(self, benchmark):
        v = Nothing()
        benchmark(lambda: v.map(lambda x: x + 1))

    def test_nothing_bind(self, benchmark):
        v = Nothing()
        benchmark(lambda: v.bind(lambda x: Some(x + 1)))

    def test_err_map(self, benchmark):
        v = Err(ValueError("x"))
        benchmark(lambda: v.map(lambda x: x + 1))

    def test_err_bind(self, benchmark):
        v = Err(ValueError("x"))
        benchmark(lambda: v.bind(lambda x: Ok(x + 1)))
