"""Monoid instances for Python built-in types."""

from __future__ import annotations

from funstruct.typeclasses.monoid import Monoid


class _IntAddMonoid(Monoid):
    def combine(self, a, b):
        return a + b

    def empty(self):
        return 0


class _IntMulMonoid(Monoid):
    def combine(self, a, b):
        return a * b

    def empty(self):
        return 1


class _StrMonoid(Monoid):
    def combine(self, a, b):
        return a + b

    def empty(self):
        return ""


class _ListMonoid(Monoid):
    def combine(self, a, b):
        return a + b

    def empty(self):
        return []


class _BoolOrMonoid(Monoid):
    def combine(self, a, b):
        return a or b

    def empty(self):
        return False


class _BoolAndMonoid(Monoid):
    def combine(self, a, b):
        return a and b

    def empty(self):
        return True


IntAddition = _IntAddMonoid()
IntMultiplication = _IntMulMonoid()
StrConcat = _StrMonoid()
ListConcat = _ListMonoid()
BoolOr = _BoolOrMonoid()
BoolAnd = _BoolAndMonoid()

__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "ListConcat",
    "BoolOr",
    "BoolAnd",
]
