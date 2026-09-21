"""Tests for AST-based do-notation — compiles yield to bind/map chains."""

from funstruct.experimental.do_ast import do_ast
from funstruct.types.cons import CList
from funstruct.types.option import Nothing, Some
from funstruct.types.result import Err, Ok


class TestDoAstResult:
    def test_basic(self):
        @do_ast
        def pipeline():
            x = yield Ok(10)
            y = yield Ok(x + 1)
            return x + y

        assert pipeline() == Ok(21)

    def test_short_circuit(self):
        @do_ast
        def pipeline():
            x = yield Ok(10)
            y = yield Err(ValueError("boom"))
            return x + y

        assert pipeline().is_err

    def test_with_args(self):
        @do_ast
        def add(a, b):
            x = yield Ok(a)
            y = yield Ok(b)
            return x + y

        assert add(3, 7) == Ok(10)


class TestDoAstOption:
    def test_some(self):
        @do_ast
        def pipeline():
            x = yield Some(5)
            y = yield Some(x * 2)
            return x + y

        assert pipeline() == Some(15)

    def test_nothing_short_circuits(self):
        @do_ast
        def pipeline():
            x = yield Some(10)
            y = yield Nothing()
            return x + y

        assert pipeline() == Nothing()


class TestDoAstCList:
    def test_cartesian_product(self):
        @do_ast
        def pipeline():
            x = yield CList.from_iterable([1, 2])
            y = yield CList.from_iterable(["a", "b"])
            return (x, y)

        assert pipeline() == CList.from_iterable([(1, "a"), (1, "b"), (2, "a"), (2, "b")])

    def test_dependent_values(self):
        @do_ast
        def pipeline():
            x = yield CList.from_iterable([1, 2, 3])
            y = yield CList.from_iterable([x, x * 10])
            return (x, y)

        assert pipeline() == CList.from_iterable([(1, 1), (1, 10), (2, 2), (2, 20), (3, 3), (3, 30)])

    def test_three_steps(self):
        @do_ast
        def pipeline():
            x = yield CList.from_iterable([1, 2])
            y = yield CList.from_iterable([10, 20])
            z = yield CList.from_iterable([100, 200])
            return x + y + z

        assert pipeline() == CList.from_iterable([111, 211, 121, 221, 112, 212, 122, 222])

    def test_guard(self):
        @do_ast
        def evens():
            x = yield CList.from_iterable(range(1, 11))
            yield CList.from_iterable([()] if x % 2 == 0 else [])
            return x

        assert evens() == CList.from_iterable([2, 4, 6, 8, 10])

    def test_with_args(self):
        @do_ast
        def pipeline(base):
            x = yield CList.from_iterable([base, base * 2])
            return x + 1

        assert pipeline(5) == CList.from_iterable([6, 11])
