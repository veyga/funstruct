"""Stringable instance for CList — human-friendly format."""

from __future__ import annotations

from funstruct.typeclasses.stringable import Stringable
from funstruct.types.cons import CList, Cons, Nil


class _CListStringable(Stringable, for_type=CList):
    def string(self, a) -> str:
        match a:
            case Nil():
                return "Nil"
            case Cons():

                def _fmt(elem) -> str:
                    match elem:
                        case CList():
                            return f"[{', '.join(_fmt(e) for e in elem)}]"
                        case _:
                            return str(elem)

                return f"CList([{', '.join(_fmt(e) for e in a)}])"
            case _:
                return str(a)
