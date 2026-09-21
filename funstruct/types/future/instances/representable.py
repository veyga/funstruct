"""Representable instance for Future."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.future import Future


class _FutureRepresentable(Representable, for_type=Future):
    def represent(self, a) -> str:
        return f"Future({a._coro})"
