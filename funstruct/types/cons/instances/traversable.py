from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.traversable import Traversable
from funstruct.types.cons import CList, Cons, Nil

_A = TypeVar("_A")
_B = TypeVar("_B")


class _CListTraversable(Traversable, for_type=CList):
    def fold_left(self, fa: CList[_A], acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        from funstruct.util.tailrec import tail_call, tco

        @tco
        def _go(current, result):
            match current:
                case Nil():
                    return result
                case Cons(h, t):
                    return tail_call(_go)(t, f(result, h))

        return _go(fa, acc)

    def fold_right(self, fa: CList[_A], acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        items = []
        current = fa
        while isinstance(current, Cons):
            items.append(current.head)
            current = current.tail
        for item in reversed(items):
            acc = f(item, acc)
        return acc

    def traverse(
        self,
        fa: CList[_A],
        f: Callable[[_A], Any],
        G: Applicative,
    ) -> Any:
        return self.fold_right(
            fa,
            G.pure(Nil()),
            lambda a, acc: G.map2(f(a), acc, lambda b, bs: Cons(b, bs)),  # type: ignore[arg-type]
        )
