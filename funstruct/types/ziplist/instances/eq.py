"""Eq instance for ZipList."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.ziplist import ZipList


class _ZipListEq(Eq, for_type=ZipList):
    def eq(self, a, b) -> bool:
        match b:
            case ZipList():
                return a._values == b._values
            case list():
                return a._values == b
            case _:
                return False

    def hash(self, a) -> int:
        return hash(tuple(a._values))
