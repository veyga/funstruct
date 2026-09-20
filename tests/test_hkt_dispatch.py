"""Tests for HKTMeta — class-level typeclass dispatch.

Methods available on a type are governed by which typeclass instances
are registered for it. HKTMeta (metaclass) handles class-level dispatch;
DotNotation handles instance-level dispatch.
"""

import pytest

from funstruct.types.either import Either, Left, Right
from funstruct.types.option import Nothing, Option, Some
from funstruct.types.result import Err, Ok, Result


class TestClassLevelDispatch:
    """HKTMeta resolves class-level calls via the typeclass registry."""

    def test_option_pure(self):
        assert Option.pure(42) == Some(42)

    def test_result_pure(self):
        assert Result.pure(42) == Ok(42)

    def test_either_pure(self):
        assert Either.pure(42) == Right(42)

    def test_option_empty(self):
        assert Option.empty() == Nothing()

    def test_result_raise_error(self):
        err = ValueError("bad")
        assert Result.raise_error(err) == Err(err)

    def test_either_raise_error(self):
        assert Either.raise_error("oops") == Left("oops")


class TestMissingInstances:
    """Types without a typeclass instance raise AttributeError for those methods."""

    def test_option_has_no_raise_error(self):
        with pytest.raises(AttributeError):
            Option.raise_error(ValueError("nope"))

    def test_option_has_no_bimap(self):
        with pytest.raises(AttributeError):
            Some(10).bimap(lambda e: e, lambda x: x)


class TestInstanceLevelDispatch:
    """DotNotation resolves instance-level calls via the typeclass registry."""

    def test_option_bind(self):
        assert Some(10).bind(lambda x: Some(x + 1)) == Some(11)

    def test_option_map(self):
        assert Some(10).map(lambda x: x * 2) == Some(20)

    def test_result_bind(self):
        assert Ok(10).bind(lambda x: Ok(x + 1)) == Ok(11)

    def test_result_handle_error_with(self):
        assert Err(ValueError("x")).handle_error_with(lambda e: Ok("recovered")) == Ok("recovered")

    def test_either_bimap(self):
        assert Right(10).bimap(lambda e: e, lambda x: x * 2) == Right(20)
        assert Left("err").bimap(lambda e: e.upper(), lambda x: x) == Left("ERR")

    def test_option_or_else(self):
        assert Nothing().or_else(Some(42)) == Some(42)
        assert Some(1).or_else(Some(42)) == Some(1)
