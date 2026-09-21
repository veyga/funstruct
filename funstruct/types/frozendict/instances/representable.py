"""Representable instance for frozendict."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.frozendict import frozendict


class _FrozendictRepresentable(Representable, for_type=frozendict):
    def represent(self, a) -> str:
        return f"frozendict({dict(a.items())})"
