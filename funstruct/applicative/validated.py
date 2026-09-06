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
from funstruct.typeclasses._dot_notation import DotNotation

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class Validated(DotNotation):
    """Base class for Valid/Invalid."""

    @abstractmethod
    def ap(self, other) -> Validated: ...

    @abstractmethod
    def product(self, other) -> Validated: ...

    def __mul__(self, other) -> Validated:
        return self.product(other)

    @property
    @abstractmethod
    def is_valid(self) -> bool: ...

    @abstractmethod
    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C: ...

    @classmethod
    def pure(cls, value) -> Validated:
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

    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        return on_valid(self.value)

    def map(self, f: Callable[[_A], _B]) -> Valid[_B]:
        return Valid(f(self.value))

    def bimap(self, on_invalid: Callable, on_valid: Callable) -> Validated:
        return Valid(on_valid(self.value))

    def left_map(self, f: Callable) -> Validated:
        return self

    def ap(self, other) -> Validated:
        match other:
            case Valid(val):
                from typing import cast
                fn = cast(Callable, self.value)
                return Valid(fn(val))
            case _:
                return other

    def product(self, other) -> Validated:
        match other:
            case Valid(val):
                return Valid((self.value, val))
            case _:
                return other


@dataclass(frozen=True)
class Invalid(Validated, Generic[_E]):
    """Failure case — accumulated errors."""

    errors: _E

    @property
    def is_valid(self) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def fold(self, on_invalid: Callable[[_E], _C], on_valid: Callable[[_A], _C]) -> _C:
        return on_invalid(self.errors)

    def bimap(self, on_invalid: Callable, on_valid: Callable) -> Validated:
        return Invalid(on_invalid(self.errors))

    def left_map(self, f: Callable) -> Validated:
        return Invalid(f(self.errors))

    def map(self, f: Callable) -> Validated:
        return self

    def ap(self, other) -> Validated:
        match other:
            case Invalid(errs):
                return Invalid(self.errors + errs)
            case _:
                return self

    def product(self, other) -> Validated:
        match other:
            case Invalid(errs):
                return Invalid(self.errors + errs)
            case _:
                return self


Validated._type_constructor = Validated
Valid._type_constructor = Validated
Invalid._type_constructor = Validated

__all__ = [
    "Validated",
    "Valid",
    "Invalid",
]
