"""Foldable — containers whose elements can be folded into a summary value.

Haskell: ``class Foldable t``
Cats: ``trait Foldable[F[_]]``

Any container that supports ``fold_right`` can derive ``fold_left``,
``to_list``, ``length``, ``is_empty``, and more.

``Foldable`` and ``Functor`` are independent — a type can be one, the
other, or both. ``Traversable`` extends both::

    Foldable    Functor
        \\       /
       Traversable

Examples::

    from funstruct.collections.cons import CList

    xs = CList.from_iterable([1, 2, 3])
    xs.fold_right(0, lambda a, acc: a + acc)  # 6
    xs.fold_left(0, lambda acc, a: acc + a)   # 6
    xs.length()                                # 3
    xs.to_list()                               # [1, 2, 3]
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")


# See _functor.py for the fa/ff/fb naming convention.


class Foldable(ABC):
    """Container whose elements can be combined into a single value.

    Subclasses must implement ``fold_right``. Other methods are derived
    but may be overridden for efficiency (e.g., CList overrides
    ``fold_left`` with a tail-recursive implementation).
    """

    @abstractmethod
    def fold_right(fa: Foldable, acc: _B, f: Callable[[_A, _B], _B]) -> _B:
        """Fold from right to left."""
        ...

    def fold_left(fa: Foldable, acc: _B, f: Callable[[_B, _A], _B]) -> _B:
        """Fold from left to right. Default via fold_right."""
        return fa.fold_right(lambda b: b, lambda a, g: lambda b: g(f(b, a)))(acc)

    def to_list(fa: Foldable) -> list:
        """Collect all elements into a Python list."""
        return (
            list(fa)
            if hasattr(fa, "__iter__")
            else fa.fold_right([], lambda a, acc: [a] + acc)
        )

    def length(fa: Foldable) -> int:
        """Count the number of elements."""
        return fa.fold_right(0, lambda _, acc: acc + 1)

    def is_empty(fa: Foldable) -> bool:
        """Check if the container has no elements."""
        return fa.length() == 0


__all__ = [
    "Foldable",
]
