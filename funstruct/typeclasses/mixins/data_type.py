"""DataType — base for all funstruct higher-kinded types.

Combines TypeConstructor (auto _type_constructor detection),
DotNotation (instance-level dispatch via summon), and
HKTMeta (class-level dispatch via summon).

    class Option(DataType, Generic[A]):
        ...

    # Instance-level: DotNotation dispatches via __getattr__
    Some(10).bind(f)       →  summon(Monad, Option).bind(Some(10), f)

    # Class-level: HKTMeta dispatches via metaclass __getattr__
    Option.pure(42)        →  summon(Applicative, Option).pure(42)
    Result.raise_error(e)  →  summon(MonadError, Result).raise_error(e)
    Option.empty()         →  summon(Alternative, Option).empty()

To create your own funstruct-compatible type:

    from funstruct.typeclasses import DataType

    class MyType(DataType, Generic[A]):
        ...

    @dataclass(frozen=True)
    class MySuccess(MyType[A]):
        value: A
"""

from __future__ import annotations

from abc import ABCMeta

from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.typeclasses.mixins.type_constructor import TypeConstructor
from funstruct.typeclasses.utils.registry import _registry

_MISSING = object()


def _dispatch(self, typeclass_type, method_name, *args):
    """Dispatch a dunder to the registered typeclass instance, or return _MISSING."""
    tc = type(self)._type_constructor or type(self)
    for (_, t), instance in _registry.items():
        if t is tc and isinstance(instance, typeclass_type):
            return getattr(instance, method_name)(self, *args)
    return _MISSING


class HKTMeta(ABCMeta):
    """Metaclass that provides class-level typeclass dispatch.

    When a class-level attribute isn't found on the type itself,
    searches the typeclass registry for an instance that provides it.
    This is the class-level counterpart to DotNotation's instance-level dispatch.

    The methods available on a type are governed entirely by which
    typeclass instances are registered for it:

        Option has _OptionMonad        → Option.pure, Option.do
        Option has _OptionAlternative  → Option.empty
        Option has _OptionTraversable  → Option.traverse, Option.sequence
        Option has NO MonadError       → Option.raise_error raises AttributeError

    Same principle as Haskell's typeclass instances or Scala's givens.
    The difference: Haskell/Scala catch missing instances at compile time;
    funstruct catches them at runtime with AttributeError.
    """

    def __getattr__(cls, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        tc = getattr(cls, "_type_constructor", None)
        if tc is None:
            for base in cls.__mro__:
                tc = getattr(base, "_type_constructor", None)
                if tc is not None:
                    break

        if tc is None:
            raise AttributeError(f"'{cls.__name__}' has no _type_constructor")

        for (_, t), instance in _registry.items():
            if t is tc and hasattr(instance, name):
                return getattr(instance, name)

        raise AttributeError(f"'{cls.__name__}' has no typeclass class method '{name}'")


class DataType(TypeConstructor, DotNotation, metaclass=HKTMeta):
    """Base for all funstruct higher-kinded types.

    Provides:
        - Auto _type_constructor detection (TypeConstructor)
        - Instance-level dispatch to typeclass instances (DotNotation)
        - Class-level dispatch to typeclass instances (HKTMeta)
        - Python dunder dispatch to typeclasses (Eq, Representable, etc.)
        - >> operator (bind via DotNotation)
        - * operator (product via DotNotation)

    Dunders delegate to typeclass instances when available,
    with sensible fallbacks when no instance is registered.
    """

    _type_constructor = None

    def __eq__(self, other: object) -> bool:
        from funstruct.typeclasses.eq import Eq

        result = _dispatch(self, Eq, "eq", other)
        return result if result is not _MISSING else NotImplemented

    def __hash__(self) -> int:
        from funstruct.typeclasses.eq import Eq

        result = _dispatch(self, Eq, "hash")
        return result if result is not _MISSING else id(self)

    def __repr__(self) -> str:
        from funstruct.typeclasses.representable import Representable

        result = _dispatch(self, Representable, "represent")
        return result if result is not _MISSING else f"{type(self).__name__}(...)"

    def __str__(self) -> str:
        from funstruct.typeclasses.stringable import Stringable

        result = _dispatch(self, Stringable, "string")
        return result if result is not _MISSING else repr(self)

    def __bool__(self) -> bool:
        from funstruct.typeclasses.truthable import Truthable

        result = _dispatch(self, Truthable, "is_truthy")
        return result if result is not _MISSING else True

    def __add__(self, other):
        from funstruct.typeclasses.semigroup import Semigroup

        result = _dispatch(self, Semigroup, "combine", other)
        return result if result is not _MISSING else NotImplemented

    def __iter__(self):
        from funstruct.typeclasses.foldable import Foldable

        tc = type(self)._type_constructor or type(self)
        for (_, t), instance in _registry.items():
            if t is tc and isinstance(instance, Foldable):
                result = []
                instance.fold_left(self, None, lambda _, a: result.append(a))
                return iter(result)
        raise TypeError(
            f"'{type(self).__name__}' is not iterable (no Foldable instance)"
        )

    def __len__(self) -> int:
        from funstruct.typeclasses.foldable import Foldable

        tc = type(self)._type_constructor or type(self)
        for (_, t), instance in _registry.items():
            if t is tc and isinstance(instance, Foldable):
                return instance.fold_left(self, 0, lambda acc, _: acc + 1)
        raise TypeError(f"'{type(self).__name__}' has no len (no Foldable instance)")


__all__ = ["DataType"]
