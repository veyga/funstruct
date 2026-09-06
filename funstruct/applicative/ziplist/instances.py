"""Typeclass instances for ZipList."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.applicative.ziplist import ZipList

_A = TypeVar("_A")
_B = TypeVar("_B")


class _ZipListApplicative(Applicative, for_type=ZipList):

    def pure(self, value: _A) -> ZipList[_A]:
        return ZipList([value])

    def ap(self, ff: ZipList[Callable[[_A], _B]], fa: ZipList[_A]) -> ZipList[_B]:
        return ZipList(f(x) for f, x in zip(ff._values, fa._values))

    def map(self, fa: ZipList[_A], f: Callable[[_A], _B]) -> ZipList[_B]:
        return ZipList(f(x) for x in fa._values)

    def map2(
        self,
        fa: ZipList[_A],
        fb: ZipList[_B],
        f: Callable[[_A, _B], object],
    ) -> ZipList:
        return ZipList(f(a, b) for a, b in zip(fa._values, fb._values))

    def product(self, fa: ZipList[_A], fb: ZipList[_B]) -> ZipList[tuple[_A, _B]]:
        return self.map2(fa, fb, lambda a, b: (a, b))
