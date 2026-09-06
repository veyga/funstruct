"""Typeclass instances for Option.

OptionMonad provides: pure, bind (primitives)
Inherits for free:    map, ap, map2, product (derived from Monad hierarchy)

OptionAlternative provides: empty, or_else

Registration is automatic — importing this module registers the instances.

    from funstruct.experimental.v2._registry import summon
    from funstruct.experimental.v2._typeclasses import Monad, Functor
    from funstruct.experimental.v2.option import Option, Some

    # These all resolve to OptionMonad:
    summon(Monad, Option).pure(42)       # Some(42)
    summon(Functor, Option).map(Some(1), str)  # Some('1')
"""

from __future__ import annotations

from funstruct.experimental.v2._registry import register
from funstruct.experimental.v2._typeclasses import Alternative, Monad
from funstruct.experimental.v2.option import Nothing, Option, Some


class OptionMonad(Monad):
    """Monad instance for Option. Only implements pure + bind.

    map, ap, map2, product are all inherited from the typeclass hierarchy.
    """

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
    """Alternative instance for Option."""

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
