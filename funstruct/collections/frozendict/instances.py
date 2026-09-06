"""Typeclass instances for frozendict."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.utils.registry import register
from funstruct.typeclasses.foldable import Foldable
from funstruct.typeclasses.functor import Functor
from funstruct.collections.frozendict import frozendict

K = TypeVar("K")
V = TypeVar("V")
V2 = TypeVar("V2")
B = TypeVar("B")


class _FrozendictFunctor(Functor):

    def map(self, fa: frozendict[K, V], f: Callable[[V], V2]) -> frozendict[K, V2]:
        return fa._map_internal(f)


class _FrozendictFoldable(Foldable):

    def fold_left(self, fa: frozendict[K, V], acc: B, f: Callable[[B, V], B]) -> B:
        return fa._fold_left_internal(acc, f)

    def fold_right(self, fa: frozendict[K, V], acc: B, f: Callable[[V, B], B]) -> B:
        return fa._fold_right_internal(acc, f)


register(Functor, frozendict, _FrozendictFunctor())
register(Foldable, frozendict, _FrozendictFoldable())
