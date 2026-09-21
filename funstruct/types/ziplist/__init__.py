"""ZipList — a list with element-wise applicative semantics.

Examples:
    >>> from funstruct.types.ziplist import ZipList
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

from collections.abc import Iterable
from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType

_A = TypeVar("_A")


class ZipList(DataType, Generic[_A]):
    """List with element-wise applicative."""

    def __init__(self, values: Iterable[_A]) -> None:
        self._values = list(values)

    def to_list(self) -> list[_A]:
        return list(self._values)


import funstruct.types.ziplist.instances  # noqa: E402, F401

__all__ = [
    "ZipList",
]
