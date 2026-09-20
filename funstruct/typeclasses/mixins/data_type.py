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
            raise AttributeError(
                f"'{cls.__name__}' has no _type_constructor"
            )

        from funstruct.typeclasses.utils.registry import _registry

        for (typeclass, t), instance in _registry.items():
            if t is tc and hasattr(instance, name):
                return getattr(instance, name)

        raise AttributeError(
            f"'{cls.__name__}' has no typeclass class method '{name}'"
        )


class DataType(TypeConstructor, DotNotation, metaclass=HKTMeta):
    """Base for all funstruct higher-kinded types.

    Provides:
        - Auto _type_constructor detection (TypeConstructor)
        - Instance-level dispatch to typeclass instances (DotNotation)
        - Class-level dispatch to typeclass instances (HKTMeta)
        - >> operator (bind)
        - * operator (product)
    """

    _type_constructor = None  # reset — DataType itself is not a type constructor


__all__ = ["DataType"]
