"""TypeConstructor — marks a class as a type constructor.

Automatically sets _type_constructor on the class and all subclasses:

    class Option(TypeConstructor, Generic[A]):  → _type_constructor = Option
    class Some(Option[A]):                      → _type_constructor = Option (inherited)
    class Nothing(Option):                      → _type_constructor = Option (inherited)

The first TypeConstructor subclass IS the type constructor.
Further subclasses (variants) inherit it.
"""

from __future__ import annotations


class TypeConstructor:
    """Marks a class as a type constructor (F[_]).

    The first subclass of TypeConstructor in the MRO is the type constructor.
    All further subclasses inherit it.

        tc_of(Some(42))  → Option
        summon(Monad, Option)  → OptionMonad
    """

    _type_constructor: type | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for base in cls.__mro__[1:]:
            if base is TypeConstructor or base is object:
                break
            tc = getattr(base, "_type_constructor", None)
            if tc is not None:
                cls._type_constructor = tc
                return
        cls._type_constructor = cls


__all__ = ["TypeConstructor"]
