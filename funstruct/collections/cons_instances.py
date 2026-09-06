"""Typeclass instances for CList."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Alternative, Monad, Traversable
from funstruct.collections.cons import CList, Cons, Nil


class CListMonad(Monad):

    def pure(self, value):
        return Cons(value)

    def bind(self, fa: CList, f):
        return fa.fold_right(Nil(), lambda a, acc: f(a).append(acc))


class CListTraversable(Traversable):

    def fold_left(self, fa: CList, acc, f):
        return fa.fold_left(acc, f)

    def fold_right(self, fa: CList, acc, f):
        return fa.fold_right(acc, f)

    def traverse(self, fa: CList, f, G):
        return fa.fold_right(
            G.pure(Nil()),
            lambda a, acc: G.map2(f(a), acc, lambda b, bs: Cons(b, bs)),
        )


class CListAlternative(Alternative):

    def pure(self, value):
        return Cons(value)

    def ap(self, ff: CList, fa: CList):
        result = Nil()
        for f in ff:
            for a in fa:
                result = Cons(f(a), result)
        return result.reversed()

    def empty(self):
        return Nil()

    def or_else(self, fa: CList, fb: CList):
        return fa.append(fb)


register(Monad, CList, CListMonad())
register(Traversable, CList, CListTraversable())
register(Alternative, CList, CListAlternative())

__all__ = ["CListMonad", "CListTraversable", "CListAlternative"]
