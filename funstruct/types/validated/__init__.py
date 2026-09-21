"""Validated: applicative error-accumulating functor.

Examples:
    >>> from funstruct.types.validated import Validated, Valid, Invalid
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

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, final

from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.types.cons import Cons

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class Validated(DataType, ABC, Generic[_E, _A]):
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


@final
@dataclass(frozen=True, eq=False, repr=False)
class Valid(Validated, Generic[_A]):
    """Success case."""

    value: _A

    @property
    def is_valid(self) -> bool:
        return True

    def fold(
        self,
        on_invalid: Callable[[_E], _C],
        on_valid: Callable[[_A], _C],
    ) -> _C:
        return on_valid(self.value)


@final
@dataclass(frozen=True, eq=False, repr=False)
class Invalid(Validated, Generic[_E]):
    """Failure case — accumulated errors."""

    errors: _E

    @property
    def is_valid(self) -> bool:
        return False

    def fold(
        self,
        on_invalid: Callable[[_E], _C],
        on_valid: Callable[[_A], _C],
    ) -> _C:
        return on_invalid(self.errors)


import funstruct.types.validated.instances  # noqa: E402, F401

__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
