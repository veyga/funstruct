from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.functor import Functor
from funstruct.types.frozendict import frozendict

K = TypeVar("K")
V = TypeVar("V")
V2 = TypeVar("V2")


class _FrozendictFunctor(Functor, for_type=frozendict):
    def map(self, fa: frozendict[K, V], f: Callable[[V], V2]) -> frozendict[K, V2]:
        return fa._map_internal(f)
