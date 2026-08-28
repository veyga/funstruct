"""Tests for Reader monad."""

from funstruct.monad.reader import Reader
from tests.laws import (
    assert_applicative_laws,
    assert_functor_laws,
    assert_monad_laws,
)


def _reader_eq(a, b):
    return a.run("ctx1") == b.run("ctx1") and a.run("ctx2") == b.run("ctx2")


class TestReaderLaws:
    def test_functor(self):
        assert_functor_laws(Reader.pure(1), eq=_reader_eq)

    def test_applicative(self):
        assert_applicative_laws(
            pure_fn=Reader.pure,
            fa=Reader.pure(1),
            fb=Reader.pure(2),
            eq=_reader_eq,
        )

    def test_monad(self):
        assert_monad_laws(
            pure_fn=Reader.pure,
            m=Reader.pure(5),
            f=lambda x: Reader.pure(x + 1),
            g=lambda x: Reader.pure(x * 10),
            eq=_reader_eq,
        )


class TestRun:
    def test_run_applies_context(self):
        r = Reader(lambda ctx: ctx + 1)
        assert r.run(5) == 6

    def test_call_is_alias(self):
        r = Reader(lambda ctx: ctx * 2)
        assert r(3) == r.run(3)


class TestMap:
    def test_map_transforms_value(self):
        r = Reader(lambda ctx: ctx * 2)
        assert r.map(lambda x: x + 1).run(5) == 11

    def test_map_preserves_context_access(self):
        r = Reader(lambda ctx: ctx)
        assert r.map(str).run(42) == "42"


class TestBind:
    def test_bind_chains(self):
        r = Reader(lambda ctx: ctx + 1)
        result = r.bind(lambda a: Reader(lambda ctx: a + ctx))
        assert result.run(10) == 21  # (10+1) + 10

    def test_bind_threads_context(self):
        get_name = Reader(lambda ctx: ctx["name"])
        get_age = Reader(lambda ctx: ctx["age"])
        combined = get_name.bind(
            lambda name: get_age.map(lambda age: f"{name} is {age}")
        )
        assert combined.run({"name": "Alice", "age": 30}) == "Alice is 30"


class TestPure:
    def test_pure_ignores_context(self):
        assert Reader.pure(42).run("anything") == 42
        assert Reader.pure(42).run(None) == 42


class TestAsk:
    def test_ask_returns_context(self):
        assert Reader.ask().run("hello") == "hello"
        assert Reader.ask().run(42) == 42

    def test_ask_with_map(self):
        assert Reader.ask().map(lambda ctx: ctx.upper()).run("hello") == "HELLO"

    def test_ask_in_pipeline(self):
        pipeline = Reader.ask().bind(lambda ctx: Reader.pure(f"got: {ctx}"))
        assert pipeline.run("env") == "got: env"


class TestOperators:
    def test_rshift_bind(self):
        r = Reader.pure(1) >> (lambda x: Reader.pure(x + 10))
        assert r.run("ctx") == 11

    def test_add_ap(self):
        r = Reader.pure(1) + Reader.pure(2)
        assert r.run("ctx") == (1, 2)
