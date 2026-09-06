"""Typeclass instances for State."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.registry import register
from funstruct.typeclasses.monad import Monad
from funstruct.monad.state import State

_A = TypeVar("_A")
_B = TypeVar("_B")


class _StateMonad(Monad):

    def pure(self, value: _A) -> State[_A]:
        return State(lambda s: (s, value))

    def bind(self, fa: State[_A], f: Callable[[_A], State[_B]]) -> State[_B]:
        def inner(s: Any) -> tuple[Any, _B]:
            new_s, a = fa._run(s)
            return f(a).run(new_s)
        return State(inner)


register(Monad, State, _StateMonad())
