"""Typeclass instances for Tree."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.collections.tree import Branch, Leaf, Tree
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.foldable import Foldable
from funstruct.typeclasses.functor import Functor
from funstruct.typeclasses.traversable import Traversable

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


class _TreeFoldable(Foldable, for_type=Tree):
    def fold_right(self, fa: Tree[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        match fa:
            case Leaf(value):
                return f(value, acc)
            case Branch(value, left, right):
                acc = self.fold_right(right, acc, f)
                acc = f(value, acc)
                acc = self.fold_right(left, acc, f)
                return acc
            case _:
                raise TypeError(f"Expected Tree, got {type(fa)}")

    def fold_left(self, fa: Tree[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        items: list[_A] = []
        self.fold_right(fa, None, lambda a, _: items.append(a))
        for item in items:
            acc = f(acc, item)
        return acc


class _TreeTraversable(Traversable, for_type=Tree):
    def fold_left(self, fa: Tree[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        items: list[_A] = []
        self.fold_right(fa, None, lambda a, _: items.append(a))
        for item in items:
            acc = f(acc, item)
        return acc

    def fold_right(self, fa: Tree[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        match fa:
            case Leaf(value):
                return f(value, acc)
            case Branch(value, left, right):
                acc = self.fold_right(right, acc, f)
                acc = f(value, acc)
                acc = self.fold_right(left, acc, f)
                return acc
            case _:
                raise TypeError(f"Expected Tree, got {type(fa)}")

    def traverse(self, fa: Tree[_A], f: Callable[[_A], Any], G: Applicative) -> Any:
        # Leaf(a) → f(a).map(Leaf)
        # Branch(v, l, r) → G.map2(G.map2(f(v), traverse(l), Branch_ctor), traverse(r), attach_right)
        match fa:
            case Leaf(value):
                return G.map(f(value), Leaf)
            case Branch(value, left, right):
                fv = f(value)
                fl = self.traverse(left, f, G)
                fr = self.traverse(right, f, G)
                return G.map2(
                    G.map2(fv, fl, lambda v, l: lambda r: Branch(v, l, r)),  # type: ignore[arg-type]
                    fr,
                    lambda build, r: build(r),  # type: ignore[arg-type,operator]
                )
            case _:
                raise TypeError(f"Expected Tree, got {type(fa)}")
