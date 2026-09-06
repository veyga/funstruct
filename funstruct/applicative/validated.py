"""Validated: applicative error-accumulating functor.

Examples:
    >>> from funstruct.applicative.validated import Validated, Valid, Invalid
    >>> Validated.cond(True, 42, "err")
    Valid(value=42)
    >>> Validated.cond(False, 42, "err")
    Invalid(errors=Cons('err', Nil()))
    >>> Valid(1) * Valid(2)
    Valid(value=(1, 2))
    >>> Invalid("a:") * Invalid("b")
    Invalid(errors='a:b')
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.collections.cons import Cons
from funstruct.typeclasses._applicative import Applicative

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class Validated(Applicative):
    """Base class for Valid/Invalid — provides constructors and supports + operator."""

    @abstractmethod
    def ap(self, other) -> Validated:
        """Apply: self contains a function, apply it to other's value.

        Accumulates errors from both sides on Invalid.
        """
        ...

    @abstractmethod
    def product(self, other) -> Validated:
        """Combine two Validated values into a tuple.

        Accumulates errors from both sides on Invalid.
        """
        ...

    def __mul__(self, other) -> Validated:
        return self.product(other)

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
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

    def __bool__(self) -> bool:
        return True

    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        """Eliminate — applies on_valid to the value."""
        return on_valid(self.value)

    def map(self, f: Callable[[_A], _B]) -> Valid[_B]:
        """Transform the success value."""
        return Valid(f(self.value))

    def ap(self, other) -> Validated:
        """Apply: self contains a function, apply it to other's value."""
        match other:
            case Valid(val):
                return Valid(self.value(val))
            case _:
                return other

    def product(self, other) -> Validated:
        """Combine two Valid values into a tuple."""
        match other:
            case Valid(val):
                return Valid((self.value, val))
            case _:
                return other



@dataclass(frozen=True)
class Invalid(Validated, Generic[_E]):
    """Failure case — accumulated errors.

    `errors` can be any Semigroup (supports +): list, str, tuple, or custom.
    """

    errors: _E

    @property
    def is_valid(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        """Eliminate — applies on_invalid to the errors."""
        return on_invalid(self.errors)

    def ap(self, other) -> Validated:
        """Apply — accumulates errors from both sides."""
        match other:
            case Invalid(errs):
                return Invalid(self.errors + errs)
            case _:
                return self

    def product(self, other) -> Validated:
        """Combine — accumulates errors from both sides."""
        match other:
            case Invalid(errs):
                return Invalid(self.errors + errs)
            case _:
                return self



__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
