"""Typeclass instances for CList."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.utils.registry import register
from funstruct.typeclasses.alternative import Alternative
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.monad import Monad
from funstruct.typeclasses.traversable import Traversable
from funstruct.collections.cons import CList, Cons, Nil

_A = TypeVar("_A")
_B = TypeVar("_B")


class _CListMonad(Monad):

    def pure(self, value: _A) -> CList[_A]:
        return Cons(value)

    def bind(self, fa: CList[_A], f: Callable[[_A], CList[_B]]) -> CList[_B]:
        return fa.fold_right(Nil(), lambda a, acc: f(a).append(acc))


class _CListTraversable(Traversable):

    def fold_left(self, fa: CList[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        return fa.fold_left(acc, f)

    def fold_right(self, fa: CList[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        return fa.fold_right(acc, f)

    def traverse(
        self,
        fa: CList[_A],
        f: Callable[[_A], object],
        G: Applicative,
    ) -> object:
        return fa.fold_right(
            G.pure(Nil()),
            lambda a, acc: G.map2(f(a), acc, lambda b, bs: Cons(b, bs)),
        )


class _CListAlternative(Alternative):

    def pure(self, value: _A) -> CList[_A]:
        return Cons(value)

    def ap(
        self,
        ff: CList[Callable[[_A], _B]],
        fa: CList[_A],
    ) -> CList[_B]:
        result: CList[_B] = Nil()
        for f in ff:
            for a in fa:
                result = Cons(f(a), result)
        return result.reversed()

    def empty(self) -> CList:
        return Nil()

    def or_else(self, fa: CList[_A], fb: CList[_A]) -> CList[_A]:
        return fa.append(fb)


register(Monad, CList, _CListMonad())
register(Traversable, CList, _CListTraversable())
register(Alternative, CList, _CListAlternative())
