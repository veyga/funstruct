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

    >>> from funstruct.monad.writer import Writer
    >>> from funstruct.typeclasses import Monoid
    >>> SetWriter = Writer.for_monoid(Monoid(typ=set, combine=lambda a, b: a | b, empty=set()))

Examples:

    >>> from funstruct.monad.writer import ListWriter
    >>> w = ListWriter(1, ["init"])
    >>> w.map(lambda x: x + 10)
    ListWriter(value=11, output=['init'])
    >>> w.bind(lambda x: ListWriter(x + 1, ["inc"]))
    ListWriter(value=2, output=['init', 'inc'])
    >>> ListWriter.pure(99)
    ListWriter(value=99, output=[])
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.collections.cons import CList, Nil
from funstruct.typeclasses.mixins.data_type import DataType
from funstruct.typeclasses.monoid import Monoid

_W = TypeVar("_W")
_A = TypeVar("_A")
_B = TypeVar("_B")


class Writer(DataType, Generic[_W, _A]):
    """Writer: (A, W) with output combined via a class-level Monoid."""

    _monoid: Monoid

    def __init__(self, value: _A, output: _W) -> None:
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "output", output)

    def bind(self, f: Callable[[_A], Writer[_W, _B]]) -> Writer[_W, _B]:
        result = f(self.value)
        return self.__class__(
            result.value,
            self._monoid.combine(self.output, result.output),
        )

    @classmethod
    def do(cls, gen_fn) -> Callable[..., Writer]:
        """Do-notation for Writer.

        >>> def pipeline():
        ...     x = yield ListWriter(1, ["init"])
        ...     y = yield ListWriter(x + 10, ["step"])
        ...     return x + y
        >>> ListWriter.do(pipeline)()
        ListWriter(value=12, output=['init', 'step'])
        """

        def _thunk(*args, **kwargs):
            gen = gen_fn(*args, **kwargs)
            try:
                first = next(gen)
                output = first.output
                value = first.value
                while True:
                    next_w = gen.send(value)
                    output = cls._monoid.combine(output, next_w.output)
                    value = next_w.value
            except StopIteration as e:
                return cls(e.value, output)

        return _thunk

    @classmethod
    def pure(cls, value) -> Writer:
        return cls(value, cls._monoid.empty)

    @classmethod
    def tell(cls, output: _W) -> Writer:
        return cls(None, output)

    def __eq__(self, other: object) -> bool:
        match other:
            case Writer(v, o):
                return self.value == v and self.output == o
            case _:
                return False

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f"{cls}(value={repr(self.value)}, output={repr(self.output)})"

    __match_args__ = ("value", "output")

    @classmethod
    def for_monoid(cls, monoid: Monoid, name: str | None = None) -> type:
        """Create a Writer subclass for a specific Monoid.

        Each returned class is its own type constructor with auto-registered
        Monad instance.

            ListWriter = Writer.for_monoid(list_monoid)
            CListWriter = Writer.for_monoid(clist_monoid)
        """
        cls_name = name or f"{monoid.typ.__name__.title()}Writer"
        new_cls = type(
            cls_name,
            (cls,),
            {
                "_monoid": monoid,
                "_type_constructor": None,
            },
        )
        new_cls._type_constructor = new_cls
        return new_cls


ListWriter = Writer.for_monoid(
    Monoid(typ=list, combine=lambda a, b: a + b, empty=[]),
    "ListWriter",
)
CListWriter = Writer.for_monoid(
    Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil()),
    "CListWriter",
)
StrWriter = Writer.for_monoid(
    Monoid(typ=str, combine=lambda a, b: a + b, empty=""),
    "StrWriter",
)
IntWriter = Writer.for_monoid(
    Monoid(typ=int, combine=lambda a, b: a + b, empty=0),
    "IntWriter",
)


import funstruct.monad.writer.instances  # noqa: E402, F401

__all__ = [
    "Writer",
    "ListWriter",
    "CListWriter",
    "StrWriter",
    "IntWriter",
]
