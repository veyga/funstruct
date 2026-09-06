"""Typeclass instance registry + summon.

Register typeclass instances for type constructors. Resolve via summon.
Derived typeclasses are resolved automatically via the hierarchy.

    register(Monad, Option, OptionMonad())

    summon(Monad, Option)       → OptionMonad()
    summon(Functor, Option)     → OptionMonad()  (derived: Monad <: Functor)
    summon(MonadError, Option)  → TypeError      (Option has no MonadError)
"""

from __future__ import annotations


_registry: dict[tuple[type, type], object] = {}


def register(typeclass: type, type_constructor: type, instance: object) -> None:
    """Register a typeclass instance for a type constructor."""
    _registry[(typeclass, type_constructor)] = instance


def summon(typeclass: type, type_constructor: type) -> object:
    """Resolve a typeclass instance for a type constructor.

    Resolution:
        1. Exact match in registry
        2. Walk registered instances — if a registered instance's typeclass
           is a subclass of the requested typeclass, return it
    """
    key = (typeclass, type_constructor)
    if key in _registry:
        return _registry[key]

    for (tc, t), instance in list(_registry.items()):
        if t is type_constructor and issubclass(tc, typeclass):
            _registry[key] = instance
            return instance

    raise TypeError(
        f"No instance of {typeclass.__name__} for {type_constructor.__name__}"
    )


def _clear_registry():
    _registry.clear()


__all__ = [
    "register",
    "summon",
]
