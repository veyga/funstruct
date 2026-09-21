from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from funstruct.typeclasses.monad import Monad
from funstruct.types.state import State

_S = TypeVar("_S")
_A = TypeVar("_A")
_B = TypeVar("_B")


class _StateMonad(Monad, for_type=State):
    def pure(self, value: _A) -> State[Any, _A]:
        return State(lambda s: (s, value))

    def bind(
        self, fa: State[_S, _A], f: Callable[[_A], State[_S, _B]]
    ) -> State[_S, _B]:
        def inner(s: _S) -> tuple[_S, _B]:
            new_s, a = fa._run(s)
            return f(a).run(new_s)

        return State(inner)
