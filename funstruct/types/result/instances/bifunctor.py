from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.types.result import Err, Ok, Result

_A = TypeVar("_A")
_B = TypeVar("_B")


class _ResultBifunctor(Bifunctor, for_type=Result):
    def bimap(
        self,
        fa: Result[_A],
        f: Callable[[Exception], Exception],
        g: Callable[[_A], _B],
    ) -> Result[_B]:
        match fa:
            case Ok(value):
                return Ok(g(value))
            case Err(error):
                return Err(f(error))
            case _:
                raise TypeError(f"Expected Result, got {type(fa)}")

    def left_map(
        self,
        fa: Result[_A],
        f: Callable[[Exception], Exception],
    ) -> Result[_A]:
        match fa:
            case Err(error):
                return Err(f(error))
            case _:
                return fa
