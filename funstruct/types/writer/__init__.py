"""Writer monad — computations with accumulated output.

Built-in Writer types (each has its own Monoid):

    ListWriter  — output: list   (combine = +, empty = [])
    CListWriter — output: CList  (combine = +, empty = Nil())
    StrWriter   — output: str    (combine = +, empty = "")
    IntWriter   — output: int    (combine = +, empty = 0)

Writer is unique among funstruct monads. Reader, State, Either, Option,
and Result all have ONE type constructor with variants. Writer has MULTIPLE
type constructors because each monoid creates a different type — ListWriter,
StrWriter, IntWriter each need their own Monad instance.

Create custom Writers with Writer.for_monoid:

    >>> from funstruct.types.writer import Writer
    >>> from funstruct.typeclasses.monoid import Monoid
    >>> class SetMonoid(Monoid):
    ...     def combine(self, a, b): return a | b
    ...     def empty(self): return set()
    >>> SetWriter = Writer.for_monoid(SetMonoid())

Examples:

    >>> from funstruct.types.writer import ListWriter
    >>> w = ListWriter(1, ["init"])
    >>> w.map(lambda x: x + 10)
    ListWriter(value=11, output=['init'])
    >>> w.bind(lambda x: ListWriter(x + 1, ["inc"]))
    ListWriter(value=2, output=['init', 'inc'])
    >>> ListWriter.pure(99)
    ListWriter(value=99, output=[])
"""

from __future__ import annotations

from typing import Generic, TypeVar

from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.typeclasses.monoid import Monoid
from funstruct.types.builtins.instances.monoid import IntAddition, ListConcat, StrConcat
from funstruct.types.cons.instances.monoid import CListConcat

_W = TypeVar("_W")
_A = TypeVar("_A")
_B = TypeVar("_B")


class Writer(DataType, Generic[_W, _A]):
    """Writer: (A, W) with output combined via a class-level Monoid."""

    _monoid: Monoid

    def __init__(self, value: _A, output: _W) -> None:
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "output", output)

    @classmethod
    def tell(cls, output: _W) -> Writer:
        return cls(None, output)  # type: ignore[arg-type]  # tell has no value

    __match_args__ = ("value", "output")

    @classmethod
    def for_monoid(cls, monoid: Monoid, name: str | None = None) -> type:
        """Create a Writer subclass for a specific Monoid.

        Writer is unique among funstruct types — its Monad instance depends
        on another typeclass (Monoid). ``bind`` needs ``Monoid.combine``,
        ``pure`` needs ``Monoid.empty``. In Cats/Scala this is resolved via
        implicits: ``given writerMonad[W: Monoid]: Monad[Writer[W, *]]``.
        Python has no implicits, so each output type needs its own concrete
        class with a registered Monad instance.

            ListWriter = Writer.for_monoid(ListConcat())
            CListWriter = Writer.for_monoid(CListConcat())
        """
        cls_name = name or f"{type(monoid).__name__}Writer"
        new_cls = type(
            cls_name,
            (cls,),
            {
                "_monoid": monoid,
                "_type_constructor": None,
            },
        )
        new_cls._type_constructor = new_cls  # type: ignore[attr-defined]  # dynamic class

        try:
            from funstruct.typeclasses.monad import Monad
            from funstruct.typeclasses.utils.registry import register
            from funstruct.types.writer.instances.monad import _WriterMonad

            register(Monad, new_cls, _WriterMonad(new_cls))

            from funstruct.typeclasses.eq import Eq
            from funstruct.typeclasses.representable import Representable
            from funstruct.types.writer.instances.eq import _WriterEq
            from funstruct.types.writer.instances.representable import (
                _WriterRepresentable,
            )

            register(Eq, new_cls, _WriterEq(new_cls))
            register(Representable, new_cls, _WriterRepresentable(new_cls))
        except ImportError:
            pass  # built-in writers registered later by instances.py

        return new_cls


ListWriter = Writer.for_monoid(ListConcat, "ListWriter")
CListWriter = Writer.for_monoid(CListConcat, "CListWriter")
StrWriter = Writer.for_monoid(StrConcat, "StrWriter")
IntWriter = Writer.for_monoid(IntAddition, "IntWriter")


import funstruct.types.writer.instances  # noqa: E402, F401

__all__ = [
    "Writer",
    "ListWriter",
    "CListWriter",
    "StrWriter",
    "IntWriter",
]
