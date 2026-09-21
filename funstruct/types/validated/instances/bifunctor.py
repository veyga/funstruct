from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses.bifunctor import Bifunctor
from funstruct.types.validated import Invalid, Valid, Validated

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class _ValidatedBifunctor(Bifunctor, for_type=Validated):
    def bimap(
        self,
        fa: Validated,
        f: Callable[[_E], _C],
        g: Callable[[_A], _B],
    ) -> Validated:
        match fa:
            case Valid(value):
                return Valid(g(value))
            case Invalid(errors):
                return Invalid(f(errors))
            case _:
                raise TypeError(f"Expected Validated, got {type(fa)}")
