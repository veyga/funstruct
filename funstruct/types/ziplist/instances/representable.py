"""Representable instance for ZipList."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.ziplist import ZipList


class _ZipListRepresentable(Representable, for_type=ZipList):
    def represent(self, a) -> str:
        return f"ZipList({a._values})"
