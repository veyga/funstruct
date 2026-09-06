"""Option — plain data type with dot-syntax via DotNotation mixin.

Option[A] = Some(value) | Nothing.

Both styles work:
    # Dot syntax (like Scala)
    Some(10).map(lambda x: x + 1)       # Some(11)
    Some(10).bind(lambda x: Some(x+1))  # Some(11)
    Nothing().map(lambda x: x + 1)      # Nothing()

    # Explicit typeclass (tagless final)
    F = summon(Monad, Option)
    F.map(Some(10), lambda x: x + 1)    # Some(11)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.experimental.v2._syntax import DotNotation

A = TypeVar("A")


class Option(DotNotation, Generic[A]):
    """Option[A] = Some(value) | Nothing."""
    pass


@dataclass(frozen=True, eq=False)
class Some(Option[A]):
    value: A

    def __eq__(self, other: object) -> bool:
        match other:
            case Some(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Some({repr(self.value)})"

    def __bool__(self) -> bool:
        return True


class Nothing(Option):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nothing)

    def __repr__(self) -> str:
        return "Nothing()"

    def __bool__(self) -> bool:
        return False


Option._type_constructor = Option
Some._type_constructor = Option
Nothing._type_constructor = Option


__all__ = ["Option", "Some", "Nothing"]
