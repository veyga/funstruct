"""Representable instance for CList."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.cons import CList, Cons, Nil


class _CListRepresentable(Representable, for_type=CList):
    def represent(self, a) -> str:
        match a:
            case Nil():
                return "Nil()"
            case Cons(head, tail):
                return f"Cons({repr(head)}, {self.represent(tail)})"
            case _:
                return f"CList({a})"
