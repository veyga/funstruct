"""Semigroup instances for Python built-in types."""

from __future__ import annotations

from funstruct.typeclasses.semigroup import Semigroup


class _IntAddSemigroup(Semigroup):
    def combine(self, a, b):
        return a + b


class _IntMulSemigroup(Semigroup):
    def combine(self, a, b):
        return a * b


class _StrSemigroup(Semigroup):
    def combine(self, a, b):
        return a + b


class _ListSemigroup(Semigroup):
    def combine(self, a, b):
        return a + b


class _BoolOrSemigroup(Semigroup):
    def combine(self, a, b):
        return a or b


class _BoolAndSemigroup(Semigroup):
    def combine(self, a, b):
        return a and b


IntAddition = _IntAddSemigroup()
IntMultiplication = _IntMulSemigroup()
StrConcat = _StrSemigroup()
ListConcat = _ListSemigroup()
BoolOr = _BoolOrSemigroup()
BoolAnd = _BoolAndSemigroup()

__all__ = [
    "IntAddition",
    "IntMultiplication",
    "StrConcat",
    "ListConcat",
    "BoolOr",
    "BoolAnd",
]
