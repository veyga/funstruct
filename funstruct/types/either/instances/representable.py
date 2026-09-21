"""Representable instance for Either."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.either import Either, Left, Right


class _EitherRepresentable(Representable, for_type=Either):
    def represent(self, a) -> str:
        match a:
            case Right(v):
                return f"Right({repr(v)})"
            case Left(e):
                return f"Left({repr(e)})"
            case _:
                return f"Either({a})"
