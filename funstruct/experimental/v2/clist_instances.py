"""Typeclass instances for CList.

CListMonad:       pure, bind → gets map, ap, product for free
CListTraversable: fold_left, fold_right, traverse → gets sequence for free
"""

from __future__ import annotations

from funstruct.experimental.v2._registry import register
from funstruct.experimental.v2._typeclasses import Monad, Traversable
from funstruct.experimental.v2.clist import CList, Cons, Nil


class CListMonad(Monad):

    def pure(self, value) -> Cons:
        return Cons(value)

    def bind(self, fa: CList, f):
        match fa:
            case Nil():
                return Nil()
            case Cons(head, tail):
                mapped_head = f(head)
                mapped_tail = self.bind(tail, f)
                return self._append(mapped_head, mapped_tail)
            case _:
                raise TypeError(f"Expected CList, got {type(fa)}")

    def _append(self, left: CList, right: CList) -> CList:
        match left:
            case Nil():
                return right
            case Cons(h, t):
                return Cons(h, self._append(t, right))


class CListTraversable(Traversable):
    """Traversable instance for CList.

    traverse takes an Applicative instance G for the target effect.
    This is cleaner than v1's pure_fn parameter.
    """

    def fold_left(self, fa: CList, acc, f):
        match fa:
            case Nil():
                return acc
            case Cons(head, tail):
                return self.fold_left(tail, f(acc, head), f)

    def fold_right(self, fa: CList, acc, f):
        match fa:
            case Nil():
                return acc
            case Cons(head, tail):
                return f(head, self.fold_right(tail, acc, f))

    def traverse(self, fa: CList, f, G):
        """(A → G[B]) → CList[A] → G[CList[B]]

        G is the Applicative instance for the target effect.
        Uses fold_right to build up the result via G.map2.
        """
        return self.fold_right(
            fa,
            G.pure(Nil()),
            lambda a, acc: G.map2(f(a), acc, lambda b, bs: Cons(b, bs)),
        )


register(Monad, CList, CListMonad())
register(Traversable, CList, CListTraversable())


__all__ = ["CListMonad", "CListTraversable"]
