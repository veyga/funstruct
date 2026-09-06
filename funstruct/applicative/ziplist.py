"""ZipList — a list with element-wise applicative semantics.

Examples:
    >>> from funstruct.applicative.ziplist import ZipList
    >>> ZipList([1, 2, 3]).map(lambda x: x * 10)
    ZipList([10, 20, 30])

    >>> ZipList.pure(lambda x: x + 1).ap(ZipList.pure(8))
    ZipList([9])

    >>> ZipList([lambda x: x + 1]).ap(ZipList([9]))
    ZipList([10])


    >>> ZipList([lambda x: x + 1, lambda x: x * 2]).ap(ZipList([10, 20]))
    ZipList([11, 40])

    >>> ZipList([1, 2]) * ZipList([3, 4])
    ZipList([(1, 3), (2, 4)])
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Generic, TypeVar

from funstruct.typeclasses._dot_notation import DotNotation

_A = TypeVar("_A")
_B = TypeVar("_B")


class ZipList(DotNotation, Generic[_A]):
    """List with element-wise applicative."""

    def __init__(self, values: Iterable[_A]) -> None:
        self._values = list(values)

    @classmethod
    def pure(cls, value: _A) -> ZipList[_A]:
        return cls([value])

    def ap(self, fa: ZipList[_A]) -> ZipList[_B]:
        """>>> ZipList([lambda x: x + 1, lambda x: x * 2]).ap(ZipList([10, 20]))
        ZipList([11, 40])
        """
        return ZipList(f(x) for f, x in zip(self._values, fa._values))

    def map(self, f: Callable[[_A], _B]) -> ZipList[_B]:
        """>>> ZipList([1, 2, 3]).map(lambda x: x * 10)
        ZipList([10, 20, 30])
        """
        return ZipList(f(x) for x in self._values)

    def map2(self, other: ZipList, f: Callable) -> ZipList:
        return ZipList(f(a, b) for a, b in zip(self._values, other._values))

    def product(self, other: ZipList) -> ZipList:
        return self.map2(other, lambda a, b: (a, b))

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


ZipList._type_constructor = ZipList

__all__ = [
    "ZipList",
]
