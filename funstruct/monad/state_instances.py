"""Typeclass instances for State."""

from __future__ import annotations

from funstruct.typeclasses._registry import register
from funstruct.typeclasses._typeclasses import Monad
from funstruct.monad.state import State


class StateMonad(Monad):

    def pure(self, value):
        return State(lambda s: (s, value))

    def bind(self, fa, f):
        def inner(s):
            new_s, a = fa._run(s)
            return f(a).run(new_s)
        return State(inner)


register(Monad, State, StateMonad())

__all__ = ["StateMonad"]
