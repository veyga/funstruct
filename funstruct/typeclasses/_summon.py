"""Backward compat — summon/register live in _registry.py now."""

from funstruct.typeclasses._registry import register as register
from funstruct.typeclasses._registry import summon as summon

__all__ = ["summon", "register"]
