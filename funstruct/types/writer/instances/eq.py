"""Eq instance for Writer."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.typeclasses.utils.registry import register
from funstruct.types.writer import (
    CListWriter,
    IntWriter,
    ListWriter,
    StrWriter,
    Writer,
)


class _WriterEq(Eq):
    def __init__(self, writer_cls: type[Writer]) -> None:
        self._cls = writer_cls

    def eq(self, a, b) -> bool:
        if not isinstance(b, Writer):
            return False
        return a.value == b.value and a.output == b.output

    def hash(self, a) -> int:
        return hash((a.value, a.output))


register(Eq, Writer, _WriterEq(Writer))
register(Eq, ListWriter, _WriterEq(ListWriter))
register(Eq, CListWriter, _WriterEq(CListWriter))
register(Eq, StrWriter, _WriterEq(StrWriter))
register(Eq, IntWriter, _WriterEq(IntWriter))
