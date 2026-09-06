"""BaseTypeclass — the root of all typeclasses in funstruct.

All typeclasses (Functor, Monad, Bifunctor, Foldable, etc.) extend this.
Provides AutoRegister: subclasses with `for_type=X` are auto-registered.

    class Functor(BaseTypeclass):           # typeclass definition
        def map(self, fa, f): ...

    class _OptionMonad(Monad, for_type=Option):   # auto-registered instance
        def pure(self, value): ...
        def bind(self, fa, f): ...
"""

from __future__ import annotations

from funstruct.typeclasses.mixins.auto_register import AutoRegister


class BaseTypeclass(AutoRegister):
    """Root of all typeclasses.

    Inheriting from BaseTypeclass gives:
        - ABC abstract method enforcement
        - AutoRegister: `for_type=X` auto-registers instances
    """
    pass


__all__ = ["BaseTypeclass"]
