"""AutoRegister — auto-register typeclass instances on class definition.

Instead of manually calling register(), declare for_type on the class:

    class _OptionMonad(Monad, for_type=Option):
        def pure(self, value): return Some(value)
        def bind(self, fa, f): ...
    # Automatically calls: register(Monad, Option, _OptionMonad())

This eliminates all register() calls from instances.py files.
"""

from __future__ import annotations

from abc import ABC


class AutoRegister(ABC):
    """Mixin that auto-registers typeclass instances via __init_subclass__.

    Any ABC that extends AutoRegister gets auto-registration for free.
    Subclasses with `for_type=SomeType` are instantiated and registered.

    The typeclass is resolved as the most specific AutoRegister parent.
    """

    def __init_subclass__(cls, for_type=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if for_type is not None:
            from funstruct.typeclasses.utils.registry import register

            typeclass = _resolve_typeclass(cls)
            register(typeclass, for_type, cls())


def _resolve_typeclass(cls: type) -> type:
    """Find the most specific typeclass parent for an instance class.

    _OptionMonad(Monad) → Monad
    _EitherBifunctor(Bifunctor) → Bifunctor
    _TreeFoldable(Foldable) → Foldable
    """
    for base in cls.__mro__[1:]:
        if base is AutoRegister or base is ABC or base is object:
            return AutoRegister
        if issubclass(base, AutoRegister) and base is not cls:
            return base
    return AutoRegister


__all__ = ["AutoRegister"]
