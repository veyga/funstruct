from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.functor import Functor
from funstruct.types.tree import Branch, Leaf, Tree

_A = TypeVar("_A")
_B = TypeVar("_B")


class _TreeFunctor(Functor, for_type=Tree):
    def map(self, fa: Tree[_A], f: Callable[[_A], _B]) -> Tree[_B]:
        match fa:
            case Leaf(value):
                return Leaf(f(value))
            case Branch(value, left, right):
                return Branch(f(value), self.map(left, f), self.map(right, f))
            case _:
                raise TypeError(f"Expected Tree, got {type(fa)}")
