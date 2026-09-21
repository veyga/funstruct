"""Representable instance for State."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.state import State


class _StateRepresentable(Representable, for_type=State):
    def represent(self, a) -> str:
        return f"State({a._run})"
