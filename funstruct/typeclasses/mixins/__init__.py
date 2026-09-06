"""Typeclass mixins — reusable base classes for data types.

DotNotation: provides dot-syntax dispatch (value.map(f)) by delegating
to the typeclass registry via __getattr__.
"""

from funstruct.typeclasses.mixins.dot_notation import DotNotation as DotNotation

__all__ = ["DotNotation"]
