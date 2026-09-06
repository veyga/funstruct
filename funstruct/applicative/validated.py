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
    def ap(ff: Validated, other) -> Validated: ...

    @abstractmethod
    def product(fa: Validated, other) -> Validated: ...

    def __mul__(self, other) -> Validated:
        return self.product(other)

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(fa: Validated, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C: ...

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

    def fold(fa: Valid, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        return on_valid(fa.value)

    def map(fa: Valid, f: Callable[[_A], _B]) -> Valid[_B]:
        return Valid(f(fa.value))

    def ap(ff: Valid, other) -> Validated:
        match other:
            case Valid(val):
                from typing import cast
                from collections.abc import Callable
                fn = cast(Callable, ff.value)
                return Valid(fn(val))
            case _:
                return other

    def product(fa: Valid, other) -> Validated:
        match other:
            case Valid(val):
                return Valid((fa.value, val))
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

    def fold(fa: Invalid, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        return on_invalid(fa.errors)

    def ap(ff: Invalid, other) -> Validated:
        match other:
            case Invalid(errs):
                return Invalid(ff.errors + errs)
            case _:
                return ff

    def product(fa: Invalid, other) -> Validated:
        match other:
            case Invalid(errs):
                return Invalid(fa.errors + errs)
            case _:
                return fa


__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
