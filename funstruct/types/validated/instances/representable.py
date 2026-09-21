"""Representable instance for Validated."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.validated import Invalid, Valid, Validated


class _ValidatedRepresentable(Representable, for_type=Validated):
    def represent(self, a) -> str:
        match a:
            case Valid(v):
                return f"Valid({repr(v)})"
            case Invalid(errors):
                return f"Invalid({repr(errors)})"
            case _:
                return f"Validated({a})"
