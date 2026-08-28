"""Functor: transform the value inside a context without changing the structure.

F[A] ---( f: A -> B )---> F[B]

When to use:
    Any time you have a value "in a box" and want to transform it without
    unwrapping. The box's structure is preserved — only the contents change.

Business examples:
    - Tree.map(format_price): format every price in a product tree
    - frozendict.map(encrypt): encrypt every value in a config dict
    - Option.map(str.upper): uppercase a name if it exists
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
