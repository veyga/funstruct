"""Option monad — presence or absence of a value.

Examples:
    >>> from funstruct.types.option import Option, Some, Nothing
    >>> from funstruct.types.cons import Cons, Nil, CList
    >>> Some(1).map(lambda x: x + 10)
    Some(11)
    >>> Nothing().bind(lambda x: Some(x * 2))
    Nothing()
    >>> Some(1) >> (lambda x: Some(x + 1))
    Some(2)
    >>> Option.from_optional(None)
    Nothing()

    map2 — combine two Options with a function:

    >>> Some(2).map2(Some(3), lambda a, b: a + b)
    Some(5)
    >>> Some(2).map2(Nothing(), lambda a, b: a + b)
    Nothing()

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Option(DataType, ABC, Generic[A]):
    """Option[A]: either Some(value) or Nothing."""

    @classmethod
    def from_optional(cls, value: A | None) -> Option[A]:
        return Nothing() if value is None else Some(value)

    @property
    @abstractmethod
    def is_some(self) -> bool: ...

    @property
    def is_nothing(self) -> bool:
        return not self.is_some

    def get_or_else(self, default: A) -> A:
        match self:
            case Some(v):
                return v
            case _:
                return default

    def filter(self, f: Callable[[A], bool]) -> Option[A]:
        match self:
            case Some(v) if f(v):
                return self
            case _:
                return Nothing()

    def fold(self, on_nothing: Callable[[], C], on_some: Callable[[A], C]) -> C:
        match self:
            case Some(v):
                return on_some(v)
            case _:
                return on_nothing()


@dataclass(frozen=True, eq=False)
class Some(Option[A]):
    """Presence of a value."""

    value: A

    @property
    def is_some(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        match other:
            case Some(val):
                return self.value == val
            case _:
                return False

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"Some({repr(self.value)})"


class Nothing(Option):
    """Absence of a value (singleton)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def is_some(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        match other:
            case Nothing():
                return True
            case _:
                return False

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Nothing()"


import funstruct.types.option.instances  # noqa: E402, F401 — register typeclass instances

__all__ = [
    "Option",
    "Some",
    "Nothing",
]
