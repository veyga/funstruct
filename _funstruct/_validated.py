"""
Validated: applicative error-accumulating functor.

Use Validated for independent validations.

Example::

    >>> from funstruct.applicative.validated import Validated
    >>> (Validated.valid(None)
    ...     .ap(Validated.invalid("too short"))
    ...     .ap(Validated.invalid("missing @")))
    Invalid(errors=Cons('too short', Cons('missing @', Nil())))

"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from _funstruct._cons import CList, Cons, Nil
from funstruct.typeclass.applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")
_E = TypeVar("_E")


class Validated(Applicative):
    """Base class for Valid/Invalid — provides constructors and supports + operator."""

    @abstractmethod
    def ap(self, other) -> Validated: ...

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(self, on_invalid: Callable, on_valid: Callable):
        """Eliminate the Validated — apply on_invalid or on_valid."""
        ...

    @classmethod
    def pure(cls, value) -> Validated:
        """Lift a value into Valid."""
        return Valid(value)

    @staticmethod
    def valid(value: _A) -> Validated:
        """Alias for pure."""
        return Valid(value)

    @staticmethod
    def invalid(error: _E) -> Validated:
        """Lift a single error into Invalid.

        Default semigroup: CList (cons list over +/append).
        For a custom semigroup, construct Invalid(your_value) directly.
        """
        return Invalid(Cons.pure(error))

    @staticmethod
    def cond(test: bool, value: _A, error: _E) -> Validated:
        """Conditional — Valid(value) if test, else Invalid(Cons(error))."""
        if test:
            return Valid(value)
        return Invalid(Cons.pure(error))


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

    def ap(self, other) -> Validated:
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

    def ap(self, other) -> Validated:
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
