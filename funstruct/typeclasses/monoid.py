"""Monoid: a Semigroup with an identity element (empty).

Laws:
  combine(empty(), a) == a  (left identity)
  combine(a, empty()) == a  (right identity)

Monoid = Semigroup + identity. The identity element lets you:
    - Start a fold with a "zero" value
    - Construct an "empty" container (Writer.pure needs this)
    - Use combine in reduce/fold without requiring non-empty input

Examples:

    >>> from funstruct.typeclasses.monoid import Monoid
    >>> class IntAdd(Monoid):
    ...     def combine(self, a, b): return a + b
    ...     def empty(self): return 0
    >>> m = IntAdd()
    >>> m.combine(1, 2)
    3
    >>> m.empty()
    0
"""

from __future__ import annotations

from abc import abstractmethod

from funstruct.typeclasses.semigroup import Semigroup


class Monoid(Semigroup):
    """A Semigroup with an identity element (empty)."""

    @abstractmethod
    def empty(self):
        # → A
        ...


__all__ = [
    "Monoid",
]
