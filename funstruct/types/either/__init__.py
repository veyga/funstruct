"""Either monad — typed error handling.

Either[E, A] = Right(a) | Left(e). Right-biased.

Examples:
    >>> from funstruct.types.either import Either, Right, Left
    >>> Right(10).map(lambda x: x + 1)
    Right(11)
    >>> Left("err").map(lambda x: x + 1)
    Left('err')
    >>> Right(10).bind(lambda x: Right(x * 2))
    Right(20)
    >>> Left("err").bind(lambda x: Right(x * 2))
    Left('err')

    handle_error_with — recover from Left:

    >>> Left("err").handle_error_with(lambda e: Right("default"))
    Right('default')
    >>> Right(10).handle_error_with(lambda e: Right("default"))
    Right(10)

    do-notation:

    >>> def pipeline():
    ...     x = yield Right(1)
    ...     y = yield Right(x + 10)
    ...     return x + y
    >>> Either.do(pipeline)()
    Right(12)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.util.created_at import CapturesCreationSiteMixin

E = TypeVar("E")
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Either(DataType, ABC, Generic[E, A]):
    """Either[E, A]: Right(value) or Left(error).

    Right-biased monad. bind/map/>> operate on the Right value
    and short-circuit on Left.
    """

    @property
    @abstractmethod
    def is_right(self) -> bool: ...

    @property
    def is_left(self) -> bool:
        return not self.is_right

    def get_or_else(self, default: A) -> A:
        match self:
            case Right(v):
                return v
            case _:
                return default

    def fold(self, on_left: Callable[[E], C], on_right: Callable[[A], C]) -> C:
        match self:
            case Right(v):
                return on_right(v)
            case Left(e):
                return on_left(e)
            case _:
                raise TypeError(f"Expected Either, got {type(self)}")

    def swap(self) -> Either[A, E]:
        match self:
            case Right(v):
                return Left(v)
            case Left(e):
                return Right(e)
            case _:
                raise TypeError(f"Expected Either, got {type(self)}")


@dataclass(frozen=True, eq=False)
class Right(Either[E, A]):
    """Success case."""

    value: A

    @property
    def is_right(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        match other:
            case Right(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Right({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Left(CapturesCreationSiteMixin, Either[E, A]):
    """Error case. Captures creation site automatically."""

    error: E

    @property
    def is_right(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        match other:
            case Left(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Left({repr(self.error)})"


import funstruct.types.either.instances  # noqa: E402, F401

__all__ = [
    "Either",
    "Right",
    "Left",
]
