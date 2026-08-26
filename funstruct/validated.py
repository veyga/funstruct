"""
Validated: applicative error-accumulating functor.

Scala Cats equivalent: ``Validated[NonEmptyList[E], A]``

Unlike Result/Either (monadic, short-circuits on first error),
Validated accumulates ALL errors via ``+`` (product).

Use Validated for independent validations that should all report.
Use Result/bind for sequential operations where later steps
depend on earlier results.

Operators::

    +   product (accumulates errors from both sides)

Example::

    >>> from funstruct.validated import Validated
    >>> Validated.valid(None) + Validated.invalid("too short") + Validated.invalid("missing @")
    Invalid(errors=['too short', 'missing @'])

"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


class Validated:
    """An Applicative used for Validation purposes"""

    @staticmethod
    def valid(value: _A) -> Valid[_A]:
        """Lift a value into Valid."""
        return Valid(value)

    @staticmethod
    def invalid(error: _E) -> Invalid[_E]:
        """Lift a single error into Invalid."""
        return Invalid([error])

    @staticmethod
    def invalid_nel(errors: list[_E]) -> Invalid[_E]:
        """Lift a list of errors into Invalid."""
        return Invalid(errors)

    @staticmethod
    def cond(test: bool, value: _A, error: _E) -> Valid[_A] | Invalid[_E]:
        """Conditional — Valid(value) if test, else Invalid([error]).

        Scala: ``Validated.cond(test, value, error)``
        """
        if test:
            return Valid(value)
        return Invalid([error])

    @staticmethod
    def cond_nel(
        test: bool, value: _A, errors: list[_E]
    ) -> Valid[_A] | Invalid[_E]:
        """Conditional with error list."""
        if test:
            return Valid(value)
        return Invalid(errors)


@dataclass(frozen=True)
class Valid(Generic[_A]):
    """Success case."""

    value: _A

    @property
    def is_valid(self) -> bool:
        return True

    @property
    def errors(self) -> list:
        return []

    def map(self, f: Callable[[_A], _B]) -> Valid[_B]:
        """Transform the success value."""
        return Valid(f(self.value))

    def product(self, other: Valid | Invalid) -> Valid | Invalid:
        """Combine with another Validated (applicative).

        Accumulates errors from both sides.
        On success, tuples the values.

        Scala: ``v1.product(v2)``
        """
        match other:
            case Valid(val):
                return Valid((self.value, val))
            case Invalid(errs):
                return Invalid(errs)

    __add__ = product

    def to_result(self):
        """Convert to returns.result.Success."""
        from returns.result import Success

        return Success(self.value)

    def to_result_or(self, exc_cls):
        """Convert to Success(value) — exc_cls unused on Valid."""
        from returns.result import Success

        return Success(self.value)


@dataclass(frozen=True)
class Invalid(Generic[_E]):
    """Failure case — accumulated errors."""

    errors: list[_E]

    @property
    def is_valid(self) -> bool:
        return False

    def map(self, f) -> Invalid[_E]:
        """No-op on Invalid."""
        return self

    def left_map(self, f: Callable[[list[_E]], list]) -> Invalid:
        """Transform the errors."""
        return Invalid(f(self.errors))

    def product(self, other: Valid | Invalid) -> Invalid:
        """Combine — accumulates errors from both sides.

        Scala: ``v1.product(v2)``
        """
        match other:
            case Valid(_):
                return self
            case Invalid(errs):
                return Invalid(self.errors + errs)

    __add__ = product

    def to_result(self):
        """Convert to returns.result.Failure."""
        from returns.result import Failure

        return Failure(self.errors)

    def to_result_or(self, exc_cls, combine=lambda errs: "; ".join(str(e) for e in errs)):
        """Convert to Failure(exc_cls(combined_errors)).

        Default combines by joining strings. Pass a custom combiner for other semigroups.
        """
        from returns.result import Failure

        return Failure(exc_cls(combine(self.errors)))


def map_n(f: Callable, *validations: Valid | Invalid) -> Valid | Invalid:
    """Apply f to all values if all valid, else accumulate errors.

    Scala: ``(v1, v2, v3).mapN(f)``

    >>> map_n(lambda a, b: a + b, Valid(1), Valid(2))
    Valid(value=3)
    >>> map_n(lambda a, b: a + b, Valid(1), Invalid(["err"]))
    Invalid(errors=['err'])
    """
    errors = []
    values = []
    for v in validations:
        match v:
            case Valid(val):
                values.append(val)
            case Invalid(errs):
                errors.extend(errs)
    if errors:
        return Invalid(errors)
    return Valid(f(*values))
