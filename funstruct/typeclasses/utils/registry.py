"""Typeclass instance registry — utilities for working with the typeclass system.

This module provides the runtime machinery for typeclass resolution.
Most users never need to call these directly — dot syntax handles
everything automatically.

When to use each function:

    register(typeclass, type_constructor, instance)
        WHO: Library authors, advanced users creating custom types
        WHEN: You've created a new data type and want it to work with
              the typeclass system (map, bind, summon, etc.)
        Example:
            class _MyMonad(Monad):
                def pure(self, value): ...
                def bind(self, fa, f): ...
            register(Monad, MyType, _MyMonad())

    summon(typeclass, type_constructor) -> instance
        WHO: Generic/effect-polymorphic program authors
        WHEN: Writing functions that work across multiple effect types
              (tagless final style). The caller summons once, the function
              uses the instance.
        Example:
            def double(F: Monad, fa):
                return F.map(fa, lambda x: x * 2)
            double(summon(Monad, Option), Some(21))

    tc_of(value) -> type
        WHO: Advanced users writing fully generic functions
        WHEN: You receive any monadic value and need to resolve its
              type constructor without knowing the concrete type.
        Example:
            def double(fa):
                F = summon(Monad, tc_of(fa))
                return F.map(fa, lambda x: x * 2)

When NOT to use these:
    - For everyday code: just use dot syntax (Some(10).map(f))
    - Inside typeclass instance methods: the instance already knows its type
    - For type checking: these resolve at runtime, not compile time
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
           (e.g. Monad registered → Functor requested → same instance)
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


def tc_of(value) -> type:
    """Get the type constructor for a value. Haskell-style automatic resolution.

    Every funstruct data type sets _type_constructor on its class:
        Some(42)  → Option
        Ok(10)    → Result
        Cons(1)   → CList
        Left("e") → Either

    Use this in generic functions for automatic typeclass resolution:

        def double(fa):
            F = summon(Monad, tc_of(fa))
            return F.map(fa, lambda x: x * 2)

        double(Some(21))  # resolves automatically → Some(42)
        double(Ok(21))    # resolves automatically → Ok(42)
    """
    tc = getattr(type(value), "_type_constructor", None)
    if tc is None:
        raise TypeError(
            f"No _type_constructor on {type(value).__name__}. "
            f"Is it a funstruct data type?"
        )
    return tc


def _clear_registry():
    _registry.clear()


__all__ = [
    "register",
    "summon",
    "tc_of",
]
