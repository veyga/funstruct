"""TypeConstructor — marks a class as a type constructor.

Automatically sets _type_constructor on the class and all subclasses:

    class Option(DataType, Generic[A]):   → _type_constructor = Option
    class Some(Option[A]):                → _type_constructor = Option (inherited)
    class Nothing(Option):                → _type_constructor = Option (inherited)

The first concrete TypeConstructor subclass IS the type constructor.
Abstract intermediaries (like DataType) that set _type_constructor = None
in their class body are skipped.
"""

from __future__ import annotations


class TypeConstructor:
    """Marks a class as a type constructor (F[_])."""

    _type_constructor: type | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # If the class explicitly declares _type_constructor = None in its
        # own __dict__, it's an abstract intermediary (e.g. DataType) — skip.
        if (
            "_type_constructor" in cls.__dict__
            and cls.__dict__["_type_constructor"] is None
        ):
            return

        # Walk MRO to find an inherited _type_constructor from a concrete parent
        for base in cls.__mro__[1:]:
            if base is TypeConstructor or base is object:
                break
            tc = base.__dict__.get("_type_constructor", None)
            if tc is not None:
                cls._type_constructor = tc
                return

        # No parent has a concrete _type_constructor — this class IS the type constructor
        cls._type_constructor = cls


__all__ = ["TypeConstructor"]
