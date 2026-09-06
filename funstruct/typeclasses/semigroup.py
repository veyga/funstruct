"""Semigroup: an associative binary combine operation over a type.

Law: combine(combine(a, b), c) == combine(a, combine(b, c))

Unlike a Protocol/ABC, this is a value — you can have multiple
Semigroup instances for the same type (e.g. int under + vs int under *).

When to use:
    Any time you need to combine/merge two values of the same type
    and the operation is associative (grouping doesn't matter).

Business examples:
    - Merging configs: combine(default_config, user_config)
    - Error accumulation in Validated: combine error lists
    - Merging frozendicts: right-biased key merge
    - Combining log entries: concatenate CList of events
    - Non-empty collections: concat where empty isn't meaningful
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Semigroup:
    """An associative binary operation over a type."""

    typ: type
    combine: Callable


__all__ = [
    "Semigroup",
]
