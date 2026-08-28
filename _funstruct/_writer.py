"""Writer monad — computations that produce a value alongside accumulated output.

Writer is abstract — subclass it with a _monoid class attribute:

    class ListWriter(Writer):
        _monoid = COMMON.LIST_CONCAT

Example::

    >>> from funstruct.monad.writer import Writer, ListWriter
    >>> ListWriter(10, ["started"]).bind(lambda x: ListWriter(x + 1, ["inc"]))
    ListWriter(value=11, output=['started', 'inc'])
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from funstruct.typeclasses._monad import Monad
from funstruct.typeclasses._monoid import Monoid

_W = TypeVar("_W")
_A = TypeVar("_A")


class Writer(Monad, Generic[_W, _A]):
    """Writer: (A, W) with output combined via a class-level Monoid.

    Subclass and set _monoid to use.
    """

    _monoid: Monoid

    __slots__ = ("value", "output")

    def __init__(self, value: _A, output: _W) -> None:
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "output", output)

    def map(self, f: Callable) -> Writer:
        """Transform the value, keep the output."""
        return self.__class__(f(self.value), self.output)

    def bind(self, f: Callable) -> Writer:
        """Chain: run f on the value, combine outputs via monoid."""
        result = f(self.value)
        return self.__class__(
            result.value,
            self._monoid.combine(self.output, result.output),
        )

    @classmethod
    def do(cls, gen_fn) -> Writer:
        """Do-notation for Writer. Accumulates output across yields."""
        gen = gen_fn()
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

    @classmethod
    def pure(cls, value) -> Writer:
        """Lift a value with empty output (uses _monoid.empty)."""
        return cls(value, cls._monoid.empty)

    @classmethod
    def tell(cls, output: _W) -> Writer:
        """Produce output with no meaningful value."""
        return cls(None, output)

    def __eq__(self, other: object) -> bool:
        match other:
            case Writer(v, o):
                return self.value == v and self.output == o
            case _:
                return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)}, output={repr(self.output)})"

    __match_args__ = ("value", "output")


__all__ = ["Writer"]
