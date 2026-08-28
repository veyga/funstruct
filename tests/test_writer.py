"""Tests for Writer monad."""

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.monad.writer import CListWriter, IntWriter, ListWriter, StrWriter
from tests.laws import assert_functor_laws, assert_monad_laws


def _writer_eq(a, b):
    return a.value == b.value and a.output == b.output


class TestWriterLaws:
    def test_functor(self):
        assert_functor_laws(ListWriter(1, []), eq=_writer_eq)

    def test_monad(self):
        assert_monad_laws(
            pure_fn=ListWriter.pure,
            m=ListWriter(5, ["init"]),
            f=lambda x: ListWriter(x + 1, ["f"]),
            g=lambda x: ListWriter(x * 10, ["g"]),
            eq=_writer_eq,
        )


class TestMap:
    def test_map_transforms_value(self):
        w = ListWriter(5, ["log"])
        assert w.map(lambda x: x * 2) == ListWriter(10, ["log"])

    def test_map_preserves_output(self):
        w = ListWriter(1, ["a", "b"])
        result = w.map(lambda x: x + 100)
        assert result.output == ["a", "b"]


class TestBind:
    def test_bind_combines_output(self):
        w = ListWriter(1, ["start"])
        result = w.bind(lambda x: ListWriter(x + 1, ["inc"]))
        assert result.value == 2
        assert result.output == ["start", "inc"]

    def test_bind_chains_multiple(self):
        w = ListWriter(0, ["init"])
        result = (
            w
            >> (lambda x: ListWriter(x + 1, ["step1"]))
            >> (lambda x: ListWriter(x + 1, ["step2"]))
        )
        assert result.value == 2
        assert result.output == ["init", "step1", "step2"]


class TestTell:
    def test_tell_writes_output(self):
        w = ListWriter.tell(["hello"])
        assert w.value is None
        assert w.output == ["hello"]

    def test_tell_in_chain(self):
        w = (
            ListWriter(1, ["start"])
            >> (lambda x: ListWriter.tell(["logged"]))
            >> (lambda _: ListWriter(42, ["done"]))
        )
        assert w.value == 42
        assert w.output == ["start", "logged", "done"]


class TestPure:
    def test_pure_has_empty_output(self):
        w = ListWriter.pure(99)
        assert w.value == 99
        assert w.output == []


class TestCustomMonoid:
    def test_string_monoid(self):
        w = StrWriter("hello", "A:")
        result = w.bind(lambda v: StrWriter(v + " world", "B:"))
        assert result.value == "hello world"
        assert result.output == "A:B:"

    def test_int_monoid(self):
        w = IntWriter("x", 1)
        result = w.bind(lambda v: IntWriter(v + "y", 1))
        assert result.value == "xy"
        assert result.output == 2


class TestEquality:
    def test_equal(self):
        assert ListWriter(1, ["a"]) == ListWriter(1, ["a"])

    def test_not_equal_value(self):
        assert ListWriter(1, ["a"]) != ListWriter(2, ["a"])

    def test_not_equal_output(self):
        assert ListWriter(1, ["a"]) != ListWriter(1, ["b"])


class TestOperators:
    def test_rshift_bind(self):
        w = ListWriter(1, ["a"]) >> (lambda x: ListWriter(x + 1, ["b"]))
        assert w.value == 2
        assert w.output == ["a", "b"]


class TestCListWriter:
    """Writer with CList output — same behavior, immutable accumulator."""

    def test_pure(self):
        w = CListWriter.pure(42)
        assert w.value == 42
        assert w.output == Nil()

    def test_bind_accumulates(self):
        w = CListWriter(1, Cons("start", Nil()))
        result = w.bind(lambda x: CListWriter(x + 1, Cons("inc", Nil())))
        assert result.value == 2
        assert result.output == Cons("start", Cons("inc", Nil()))

    def test_chain(self):
        w = (
            CListWriter(0, Cons("init", Nil()))
            >> (lambda x: CListWriter(x + 1, Cons("step1", Nil())))
            >> (lambda x: CListWriter(x + 1, Cons("step2", Nil())))
        )
        assert w.value == 2
        assert w.output == CList.from_iterable(["init", "step1", "step2"])

    def test_tell(self):
        w = CListWriter.tell(Cons("logged", Nil()))
        assert w.value is None
        assert w.output == Cons("logged", Nil())

    def test_map_preserves_output(self):
        w = CListWriter(5, Cons("a", Nil()))
        result = w.map(lambda x: x * 2)
        assert result.value == 10
        assert result.output == Cons("a", Nil())

    def test_monad_laws(self):
        assert_monad_laws(
            pure_fn=CListWriter.pure,
            m=CListWriter(5, Cons("init", Nil())),
            f=lambda x: CListWriter(x + 1, Cons("f", Nil())),
            g=lambda x: CListWriter(x * 10, Cons("g", Nil())),
            eq=_writer_eq,
        )
