"""Representable instance for Writer."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.typeclasses.utils.registry import register
from funstruct.types.writer import (
    CListWriter,
    IntWriter,
    ListWriter,
    StrWriter,
    Writer,
)


class _WriterRepresentable(Representable):
    def __init__(self, writer_cls: type[Writer]) -> None:
        self._cls = writer_cls

    def represent(self, a) -> str:
        cls_name = type(a).__name__
        return f"{cls_name}(value={repr(a.value)}, output={repr(a.output)})"


register(Representable, Writer, _WriterRepresentable(Writer))
register(Representable, ListWriter, _WriterRepresentable(ListWriter))
register(Representable, CListWriter, _WriterRepresentable(CListWriter))
register(Representable, StrWriter, _WriterRepresentable(StrWriter))
register(Representable, IntWriter, _WriterRepresentable(IntWriter))
