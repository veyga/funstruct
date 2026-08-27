"""
Validated: applicative error-accumulating functor.

Scala Cats equivalent: ``Validated[NonEmptyList[E], A]``

Unlike Result/Either (monadic, short-circuits on first error),
Validated accumulates ALL errors via .product() / .map_n().

Use Validated for independent validations that should all report.
Use Result/bind for sequential operations where later steps
depend on earlier results.

Example::

    >>> from jf_commons.functional.validated import Validated
    >>> (Validated.valid(None)
    ...     .product(Validated.invalid("too short"))
    ...     .product(Validated.invalid("missing @")))
    Invalid(errors=['too short', 'missing @'])

"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from _funstruct._functor import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


class Validated(Applicative):
    """Base class for Valid/Invalid — provides constructors and supports + operator."""

    @abstractmethod
    def product(self, other: Validated) -> Validated: ...

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(self, on_invalid: Callable, on_valid: Callable):
        """Eliminate the Validated — apply on_invalid or on_valid."""
        ...

    @staticmethod
    def valid(value: _A) -> Validated:
        """Lift a value into Valid."""
        return Valid(value)

    @staticmethod
    def invalid(error: _E) -> Validated:
        """Lift a single error into Invalid."""
        return Invalid([error])

    @staticmethod
    def invalid_nel(errors: list[_E]) -> Validated:
        """Lift a list of errors into Invalid."""
        return Invalid(errors)

    @staticmethod
    def cond(test: bool, value: _A, error: _E) -> Validated:
        """Conditional — Valid(value) if test, else Invalid([error])."""
        if test:
            return Valid(value)
        return Invalid([error])

    @staticmethod
    def cond_nel(test: bool, value: _A, errors: list[_E]) -> Validated:
        """Conditional with error list."""
        if test:
            return Valid(value)
        return Invalid(errors)


@dataclass(frozen=True)
class Valid(Validated, Generic[_A]):
    """Success case."""

    value: _A

    @property
    def is_valid(self) -> bool:
        return True

    def fold(self, on_invalid: Callable, on_valid: Callable):
        """Eliminate — applies on_valid to the value."""
        return on_valid(self.value)

    def map(self, f: Callable[[_A], _B]) -> Valid[_B]:
        """Transform the success value."""
        return Valid(f(self.value))

    def product(self, other: Validated) -> Validated:
        """Combine with another Validated (applicative).

        Accumulates errors from both sides.
        On success, tuples the values.
        """
        match other:
            case Valid(val):
                return Valid((self.value, val))
            case _:
                return other

    def to_result(self):
        """Convert to returns.result.Success."""
        from returns.result import Success

        return Success(self.value)


@dataclass(frozen=True)
class Invalid(Validated, Generic[_E]):
    """Failure case — accumulated errors.

    `errors` can be any Semigroup (supports +): list, str, tuple, or custom.
    """

    errors: _E

    @property
    def is_valid(self) -> bool:
        return False

    def map(self, f) -> Invalid[_E]:
        """No-op on Invalid."""
        return self

    def fold(self, on_invalid: Callable, on_valid: Callable):
        """Eliminate — applies on_invalid to the errors."""
        return on_invalid(self.errors)

    def product(self, other: Validated) -> Validated:
        """Combine — accumulates errors from both sides."""
        match other:
            case Invalid(errs):
                return Invalid(self.errors + errs)
            case _:
                return self

    def to_result(self):
        """Convert to returns.result.Failure."""
        from returns.result import Failure

        return Failure(self.errors)


__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
