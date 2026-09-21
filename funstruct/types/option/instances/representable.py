"""Representable instance for Option."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.option import Nothing, Option, Some


class _OptionRepresentable(Representable, for_type=Option):
    def represent(self, a) -> str:
        match a:
            case Some(v):
                return f"Some({repr(v)})"
            case Nothing():
                return "Nothing()"
            case _:
                return f"Option({a})"
