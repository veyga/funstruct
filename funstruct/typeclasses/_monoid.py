"""Monoid: a Semigroup with an identity element (empty).

Laws:
  combine(empty, a) == a  (left identity)
  combine(a, empty) == a  (right identity)

Monoid = Semigroup + identity. The identity element lets you:
    - Start a fold with a "zero" value
    - Construct an "empty" container (Writer.pure needs this)
    - Use combine in reduce/fold without requiring non-empty input

When to use (vs Semigroup):
    Use Monoid when you need a starting point / default / empty.
    Use Semigroup when you only ever combine existing values.

Business examples:
    - Writer output: start with empty log, accumulate entries
    - Fold over a collection: sum([], start=0), concat([], start="")
    - Default config: empty config is the identity for merge
    - Counters/metrics: start at 0, combine by addition
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import final

from funstruct.typeclasses._semigroup import Semigroup


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
