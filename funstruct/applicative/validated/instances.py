"""Typeclass instances for Validated."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, cast

from funstruct.applicative.validated import Invalid, Valid, Validated
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.bifunctor import Bifunctor

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_E = TypeVar("_E")


class _ValidatedApplicative(Applicative, for_type=Validated):
    def pure(self, value: _A) -> Valid[_A]:
        return Valid(value)

    def ap(self, ff: Validated, fa: Validated) -> Validated:
        match ff, fa:
            case Valid(f_val), Valid(a_val):
                fn = cast(Callable, f_val)
                return Valid(fn(a_val))
            case Invalid(errs1), Invalid(errs2):
                return Invalid(errs1 + errs2)
            case Invalid(), _:
                return ff
            case _, Invalid():
                return fa
            case _:
                raise TypeError(f"Expected Validated, got {type(ff)}, {type(fa)}")

    def map(self, fa: Validated, f: Callable[[_A], _B]) -> Validated:
        match fa:
            case Valid(value):
                return Valid(f(value))
            case Invalid():
                return fa
            case _:
                raise TypeError(f"Expected Validated, got {type(fa)}")

    def product(self, fa: Validated, fb: Validated) -> Validated:
        match fa, fb:
            case Valid(a_val), Valid(b_val):
                return Valid((a_val, b_val))
            case Invalid(errs1), Invalid(errs2):
                return Invalid(errs1 + errs2)
            case Invalid(), _:
                return fa
            case _, Invalid():
                return fb
            case _:
                raise TypeError(f"Expected Validated, got {type(fa)}, {type(fb)}")


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
