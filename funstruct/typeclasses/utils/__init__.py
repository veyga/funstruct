"""Typeclass utilities — runtime machinery for typeclass resolution.

These are NOT typeclasses. They are tools for working with the typeclass system.

    register: declare a typeclass instance for a type constructor
    summon:   resolve a typeclass instance from the registry
    tc_of:    get the type constructor from a value (Haskell-style resolution)
"""

from funstruct.typeclasses.utils.registry import register as register
from funstruct.typeclasses.utils.registry import summon as summon
from funstruct.typeclasses.utils.registry import tc_of as tc_of

__all__ = ["register", "summon", "tc_of"]
