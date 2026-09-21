"""Representable instance for Tree."""

from __future__ import annotations

from funstruct.typeclasses.representable import Representable
from funstruct.types.tree import Branch, Leaf, Tree


class _TreeRepresentable(Representable, for_type=Tree):
    def represent(self, a) -> str:
        match a:
            case Leaf(v):
                return f"Leaf({repr(v)})"
            case Branch(v, left, right):
                return f"Branch({repr(v)}, {repr(left)}, {repr(right)})"
            case _:
                return f"Tree({a})"
