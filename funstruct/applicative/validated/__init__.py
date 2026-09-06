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
from funstruct.typeclasses.mixins.data_type import DataType

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class Validated(DataType, Generic[_E, _A]):
    """Base class for Valid/Invalid. Bifunctor over error and value types."""

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(
        self,
        on_invalid: Callable[[_E], _C],
        on_valid: Callable[[_A], _C],
    ) -> _C: ...

    def __mul__(self, other: Validated) -> Validated:
        return self.product(other)

    @classmethod
    def pure(cls, value: _A) -> Validated:
        return Valid(value)

    @staticmethod
    def valid(value: _A) -> Validated:
        return Valid(value)

    @staticmethod
    def invalid(error: _E) -> Validated:
        return Invalid(Cons.pure(error))

    @staticmethod
    def cond(test: bool, value: _A, error: _E) -> Validated:
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

    def fold(
        self,
        on_invalid: Callable[[_E], _C],
        on_valid: Callable[[_A], _C],
    ) -> _C:
        return on_valid(self.value)


@dataclass(frozen=True)
class Invalid(Validated, Generic[_E]):
    """Failure case — accumulated errors."""

    errors: _E

    @property
    def is_valid(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def fold(
        self,
        on_invalid: Callable[[_E], _C],
        on_valid: Callable[[_A], _C],
    ) -> _C:
        return on_invalid(self.errors)



import funstruct.applicative.validated.instances  # noqa: E402, F401

__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
