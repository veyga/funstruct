"""Result — plain data type with dot-syntax via DotNotation mixin.

Result[A] = Ok(value) | Err(exception).

Both styles work:
    # Dot syntax
    Ok(10).map(lambda x: x + 1)   # Ok(11)
    Ok(10).bind(lambda x: Ok(x))  # Ok(10)

    # Explicit typeclass
    F = summon(MonadError, Result)
    F.raise_error(ValueError("x"))  # Err(ValueError('x'))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.experimental.v2._syntax import DotNotation

A = TypeVar("A")


class Result(DotNotation, Generic[A]):
    """Result[A] = Ok(value) | Err(exception)."""
    pass


@dataclass(frozen=True, eq=False)
class Ok(Result[A]):
    value: A

    def __eq__(self, other: object) -> bool:
        match other:
            case Ok(val):
                return self.value == val
            case _:
                return False

    def __repr__(self) -> str:
        return f"Ok({repr(self.value)})"


@dataclass(frozen=True, eq=False)
class Err(Result[A]):
    error: Exception

    def __eq__(self, other: object) -> bool:
        match other:
            case Err(err):
                return self.error == err
            case _:
                return False

    def __repr__(self) -> str:
        return f"Err({repr(self.error)})"


Result._type_constructor = Result
Ok._type_constructor = Result
Err._type_constructor = Result


__all__ = ["Result", "Ok", "Err"]
