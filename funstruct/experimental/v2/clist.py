"""CList — plain cons list data type. No typeclass methods.

CList[A] = Cons(head, tail) | Nil.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from funstruct.experimental.v2._syntax import DotNotation

A = TypeVar("A")


class CList(DotNotation, Generic[A]):
    """Singly linked cons list."""
    pass


@dataclass(frozen=True, eq=False)
class Cons(CList[A]):
    head: A
    tail: CList[A] = field(default_factory=lambda: Nil())

    def __eq__(self, other: object) -> bool:
        match other:
            case Cons(h, t):
                return self.head == h and self.tail == t
            case _:
                return False

    def __repr__(self) -> str:
        return f"Cons({repr(self.head)}, {repr(self.tail)})"

    def __bool__(self) -> bool:
        return True


class Nil(CList):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nil)

    def __repr__(self) -> str:
        return "Nil()"

    def __bool__(self) -> bool:
        return False


CList._type_constructor = CList
Cons._type_constructor = CList
Nil._type_constructor = CList


def from_list(xs: list) -> CList:
    result = Nil()
    for x in reversed(xs):
        result = Cons(x, result)
    return result


__all__ = ["CList", "Cons", "Nil", "from_list"]
