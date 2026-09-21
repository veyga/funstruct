"""Representable instance for Reader."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.reader import Reader


class _ReaderRepresentable(Representable, for_type=Reader):
    def represent(self, a) -> str:
        return f"Reader({a._run})"
