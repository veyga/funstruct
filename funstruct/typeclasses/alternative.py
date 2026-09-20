"""Alternative — a monoid on applicative functors.

empty:   F[A]             — the zero/identity element
or_else: F[A] → F[A] → F[A] — try fa, if it's empty/failed try fb

Laws (same as Monoid, lifted into F):
    or_else(empty, fa) == fa        (left identity)
    or_else(fa, empty) == fa        (right identity)
    or_else(a, or_else(b, c)) == or_else(or_else(a, b), c)  (associativity)

Examples:

    Option — fallback chains:

    >>> from funstruct.monad.option import Some, Nothing
    >>> Some(1).or_else(Some(2))
    Some(1)
    >>> Nothing().or_else(Some(2))
    Some(2)
    >>> Nothing().or_else(Nothing()).or_else(Some(3))
    Some(3)

    CList — concatenation (Alternative for lists is append):

    >>> from funstruct.collections.cons import CList, Nil
    >>> CList.new(1, 2).or_else(CList.new(3, 4)).to_list()
    [1, 2, 3, 4]
    >>> Nil().or_else(CList.new(1)).to_list()
    [1]
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from funstruct.typeclasses.applicative import Applicative


class Alternative(Applicative):
    """empty + or_else — a monoid on applicative functors."""

    @abstractmethod
    def empty(self) -> Any:
        # → F[A]
        ...

    @abstractmethod
    def or_else(self, fa, fb) -> Any:
        # fa: F[A], fb: F[A] → F[A]
        ...


__all__ = ["Alternative"]
