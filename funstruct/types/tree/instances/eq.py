"""Eq instance for Tree."""

from __future__ import annotations

from funstruct.typeclasses.eq import Eq
from funstruct.types.tree import Branch, Leaf, Tree


class _TreeEq(Eq, for_type=Tree):
    def eq(self, a, b) -> bool:
        match a, b:
            case Leaf(va), Leaf(vb):
                return va == vb
            case Branch(va, la, ra), Branch(vb, lb, rb):
                return va == vb and la == lb and ra == rb
            case _:
                return False

    def hash(self, a) -> int:
        match a:
            case Leaf(v):
                return hash(("Leaf", v))
            case Branch(v, l, r):
                return hash(("Branch", v, hash(l), hash(r)))
            case _:
                return hash(id(a))
