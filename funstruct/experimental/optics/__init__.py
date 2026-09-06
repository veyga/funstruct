"""Optics — composable getters and setters for immutable data.

Lenses let you read and update deeply nested immutable structures
without manually rebuilding the path at every level.

Examples:
    >>> from funstruct.experimental.optics import Lens, at
    >>> from funstruct.collections.frozendict import frozendict
    >>> users = frozendict({
    ...     "alice": {"profile": {"age": 30, "city": "NYC"}},
    ... })
    >>> age_lens = at("alice") >> at("profile") >> at("age")
    >>> age_lens.get(users)
    30
    >>> age_lens.set(users, 31)["alice"]["profile"]["age"]
    31
    >>> age_lens.modify(users, lambda x: x + 1)["alice"]["profile"]["age"]
    31

Status: experimental. API may change.
"""

from funstruct.experimental.optics._lens import Lens as Lens
from funstruct.experimental.optics._lens import at as at

__all__ = [
    "Lens",
    "at",
]
