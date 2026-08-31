"""Functor: anything that can be mapped over.

If you have a value inside some context (a list, an Option, an Either,
a Tree), `.map(f)` applies `f` to the value without changing the structure.

::

    F[A] ---( f: A -> B )---> F[B]

Examples:
    >>> from funstruct.monad.option import Some, Nothing
    >>> Some(5).map(lambda x: x * 2)
    Some(10)
    >>> Nothing().map(lambda x: x * 2)
    Nothing()

The structure is preserved — Some stays Some, Nothing stays Nothing.
Only the contents change.

Laws:
    - Identity: ``x.map(lambda a: a) == x``
    - Composition: ``x.map(f).map(g) == x.map(lambda a: g(f(a)))``

Types that are Functors:
    - Option — map over the value if present
    - Either — map over the Right value
    - Result — map over the Ok value
    - Cons — map over every element
    - Tree — map over every node
    - frozendict — map over every value

See also:
    `Haskell wiki: Functor <https://wiki.haskell.org/Functor>`_
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

_A = TypeVar("_A")
_B = TypeVar("_B")


class Functor(ABC, Generic[_A]):
    """Transform the value inside a context.

    Type parameter:
        _A: The value type inside the functor.
    """

    @abstractmethod
    def map(self, f: Callable[[_A], _B]) -> Functor[_B]: ...


__all__ = [
    "Functor",
]
