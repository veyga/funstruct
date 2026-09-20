"""DataType — base for all funstruct data types.

Combines TypeConstructor (auto _type_constructor detection) and
DotNotation (dot-syntax dispatch via summon).

    class Option(DataType, Generic[A]):
        ...

    class Either(DataType, Generic[E, A]):
        ...

To create your own funstruct-compatible type:

    from funstruct.typeclasses import DataType

    class MyType(DataType, Generic[A]):
        ...

    @dataclass(frozen=True)
    class MySuccess(MyType[A]):
        value: A
"""

from __future__ import annotations

from funstruct.typeclasses.mixins.dot_notation import DotNotation
from funstruct.typeclasses.mixins.type_constructor import TypeConstructor


class DataType(TypeConstructor, DotNotation):
    """Base for all funstruct data types.

    Provides:
        - Auto _type_constructor detection (TypeConstructor)
        - Dot-syntax dispatch to registered typeclass instances (DotNotation)
        - >> operator (bind)
        - * operator (product)
        - do (class-level, delegates to Monad instance)
    """

    _type_constructor = None  # reset — DataType itself is not a type constructor

    @classmethod
    def do(cls, gen_fn):
        """Do-notation — delegates to summon(Monad, cls).do."""
        from funstruct.typeclasses.monad import Monad
        from funstruct.typeclasses.utils.registry import _registry

        tc = cls._type_constructor or cls
        for (typeclass, t), instance in _registry.items():
            if t is tc and isinstance(instance, Monad):
                return instance.do(gen_fn)
        raise TypeError(f"No Monad instance registered for {tc.__name__}")


__all__ = ["DataType"]
