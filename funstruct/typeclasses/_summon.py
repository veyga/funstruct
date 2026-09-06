"""summon — typeclass instance resolution.

Resolves which type provides a given typeclass for a given type constructor.
Walks the inheritance hierarchy to derive parent typeclasses automatically.

    summon(Monad, Option)       → Option   (Option extends Monad)
    summon(Functor, Option)     → Option   (derived: Monad <: Applicative <: Functor)
    summon(MonadError, Result)  → Result   (Result extends MonadError)
    summon(MonadError, Option)  → raises   (Option is not a MonadError)

In Scala, this is ``implicitly[Monad[Option]]`` or ``summon[Monad[Option]]``.

The key insight: since funstruct types inherit from their typeclasses,
the type constructor IS the instance. ``summon(Monad, Option)`` returns
``Option`` itself — it already has ``pure``, ``bind``, ``map``, ``ap``.

TypeConstructor:
    In Haskell/Scala, ``F[_]`` represents a type constructor — a type that
    takes a type parameter. Python has no native HKT support, but since our
    types inherit from their typeclasses, the class itself serves as the
    type constructor:

        F = Option          # F[_] = Option
        F.pure(42)          # Option.pure(42) → Some(42)
        F.pure(42).map(f)   # Some(42).map(f) → Some(f(42))

    This lets you write effect-polymorphic code:

        def program[F: Monad](F):
            return F.pure(42).bind(lambda x: F.pure(x + 1))

        program(Option)  # Some(43)
        program(Result)  # Ok(43)
"""

from __future__ import annotations

from typing import TypeVar

_TC = TypeVar("_TC")
_T = TypeVar("_T")

_registry: dict[tuple[type, type], type] = {}


def register(typeclass: type, type_constructor: type, instance: type | None = None) -> None:
    """Register a typeclass instance for a type constructor.

    If instance is None, the type constructor itself is used (the common
    case when the type inherits from the typeclass).
    """
    _registry[(typeclass, type_constructor)] = instance or type_constructor


def summon(typeclass: type[_TC], type_constructor: type[_T]) -> type:
    """Resolve a typeclass instance for a type constructor.

    Resolution order:
        1. Exact match in the registry
        2. Inheritance check (issubclass)
        3. Walk registered supertypes of the typeclass

    Raises TypeError if no instance can be found.

    >>> from funstruct.typeclasses._monad import Monad
    >>> from funstruct.typeclasses._functor import Functor
    >>> from funstruct.monad.option import Option
    >>> summon(Monad, Option) is Option
    True
    >>> summon(Functor, Option) is Option
    True
    """
    key = (typeclass, type_constructor)
    if key in _registry:
        return _registry[key]

    if issubclass(type_constructor, typeclass):
        _registry[key] = type_constructor
        return type_constructor

    for (tc, t), instance in list(_registry.items()):
        if t is type_constructor and issubclass(tc, typeclass):
            _registry[key] = instance
            return instance

    raise TypeError(
        f"No instance of {typeclass.__name__} for {type_constructor.__name__}. "
        f"{type_constructor.__name__} does not extend {typeclass.__name__}."
    )


__all__ = [
    "summon",
    "register",
]
