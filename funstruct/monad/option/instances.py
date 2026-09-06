"""Typeclass instances for Option."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Alternative, Monad
from funstruct.monad.option import Nothing, Option, Some

_A = TypeVar("_A")
_B = TypeVar("_B")


class _OptionMonad(Monad):

    def pure(self, value: _A) -> Option[_A]:
        return Some(value)

    def bind(self, fa: Option[_A], f: Callable[[_A], Option[_B]]) -> Option[_B]:
        match fa:
            case Some(value):
                return f(value)
            case Nothing():
                return fa
            case _:
                raise TypeError(f"Expected Option, got {type(fa)}")


class _OptionAlternative(Alternative):

    def pure(self, value: _A) -> Option[_A]:
        return Some(value)

    def ap(
        self,
        ff: Option[Callable[[_A], _B]],
        fa: Option[_A],
    ) -> Option[_B]:
        match ff:
            case Some(f):
                match fa:
                    case Some(val):
                        return Some(f(val))
                    case _:
                        return Nothing()
            case _:
                return Nothing()

    def empty(self) -> Option:
        return Nothing()

    def or_else(self, fa: Option[_A], fb: Option[_A]) -> Option[_A]:
        match fa:
            case Some():
                return fa
            case Nothing():
                return fb


register(Monad, Option, _OptionMonad())
register(Alternative, Option, _OptionAlternative())
