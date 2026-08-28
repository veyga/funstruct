"""
Monoid: a Semigroup with an identity element.

Laws:
  combine(empty, a) == a  (left identity)
  combine(a, empty) == a  (right identity)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from funstruct.typeclasses._semigroup import Semigroup


from typing import final


@final
@dataclass(frozen=True)
class Monoid(Semigroup):
    """A Semigroup with an identity element (empty)."""

    typ: type
    combine: Callable
    empty: object


__all__ = [
    "Monoid",
]
