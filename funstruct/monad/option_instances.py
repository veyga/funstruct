"""Typeclass instances for Option.

OptionMonad: pure + bind (primitives). map, ap, map2, product derived.
OptionAlternative: pure + ap + empty + or_else.

Importing this module registers the instances.
"""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Alternative, Monad
from funstruct.monad.option import Nothing, Option, Some


class OptionMonad(Monad):

    def pure(self, value) -> Some:
        return Some(value)

    def bind(self, fa: Option, f):
        match fa:
            case Some(value):
                return f(value)
            case Nothing():
                return fa
            case _:
                raise TypeError(f"Expected Option, got {type(fa)}")


class OptionAlternative(Alternative):

    def pure(self, value) -> Some:
        return Some(value)

    def ap(self, ff: Option, fa: Option):
        match ff:
            case Some(f):
                match fa:
                    case Some(val):
                        return Some(f(val))
                    case _:
                        return Nothing()
            case _:
                return Nothing()

    def empty(self) -> Nothing:
        return Nothing()

    def or_else(self, fa: Option, fb: Option):
        match fa:
            case Some():
                return fa
            case Nothing():
                return fb


register(Monad, Option, OptionMonad())
register(Alternative, Option, OptionAlternative())


__all__ = ["OptionMonad", "OptionAlternative"]
