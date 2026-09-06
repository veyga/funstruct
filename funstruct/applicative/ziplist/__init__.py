"""ZipList — a list with element-wise applicative semantics.

Examples:
    >>> from funstruct.applicative.ziplist import ZipList
    >>> ZipList([1, 2, 3]).map(lambda x: x * 10)
    ZipList([10, 20, 30])

    >>> ZipList([lambda x: x + 1]).ap(ZipList([9]))
    ZipList([10])

    >>> ZipList([lambda x: x + 1, lambda x: x * 2]).ap(ZipList([10, 20]))
    ZipList([11, 40])

    >>> ZipList([1, 2]) * ZipList([3, 4])
    ZipList([(1, 3), (2, 4)])
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.typeclasses.mixins.type_constructor import TypeConstructor

_A = TypeVar("_A")


class ZipList(TypeConstructor, DotNotation, Generic[_A]):
    """List with element-wise applicative."""

    def __init__(self, values: Iterable[_A]) -> None:
        self._values = list(values)

    @classmethod
    def pure(cls, value: _A) -> ZipList[_A]:
        return cls([value])

    def __mul__(self, other: ZipList) -> ZipList:
        return self.product(other)

    def to_list(self) -> list[_A]:
        return list(self._values)

    def __iter__(self) -> Iterator[_A]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: object) -> bool:
        match other:
            case ZipList():
                return self._values == other._values
            case list():
                return self._values == other
            case _:
                return False

    def __repr__(self) -> str:
        return f"ZipList({self._values})"



import funstruct.applicative.ziplist.instances  # noqa: E402, F401

__all__ = [
    "ZipList",
]
