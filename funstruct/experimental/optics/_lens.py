"""Lens — a composable getter/setter for immutable structures.

A Lens[S, A] focuses on a value of type A inside a structure of type S.

    get:    S -> A
    set:    (S, A) -> S
    modify: (S, A -> A) -> S

Compose with >> to focus deeper:

    at("user") >> at("profile") >> at("age")

This builds a single lens that reads/writes age through the
entire path, rebuilding intermediate structures on set.

Scala/Cats: ``monocle.Lens``
Haskell:    ``Control.Lens``
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

_S = TypeVar("_S")
_A = TypeVar("_A")
_B = TypeVar("_B")


@dataclass(frozen=True)
class Lens:
    """A composable getter/setter pair.

    >>> from funstruct.collections.frozendict import frozendict
    >>> fd = frozendict({"a": frozendict({"b": 1})})
    >>> lens = at("a") >> at("b")
    >>> lens.get(fd)
    1
    >>> lens.set(fd, 99)["a"]["b"]
    99
    >>> lens.modify(fd, lambda x: x + 1)["a"]["b"]
    2
    """

    _get: Callable
    _set: Callable

    def get(self, s):
        return self._get(s)

    def set(self, s, value):
        return self._set(s, value)

    def modify(self, s, f: Callable):
        return self.set(s, f(self.get(s)))

    def __rshift__(self, other: Lens) -> Lens:
        return _compose(self, other)


def _compose(outer: Lens, inner: Lens) -> Lens:
    return Lens(
        _get=lambda s: inner.get(outer.get(s)),
        _set=lambda s, v: outer.set(s, inner.set(outer.get(s), v)),
    )


def at(key) -> Lens:
    """Create a lens that focuses on a key in a dict-like structure.

    Works with frozendict (uses put) and plain dicts (uses spread).

    >>> from funstruct.collections.frozendict import frozendict
    >>> lens = at("x")
    >>> lens.get(frozendict({"x": 42}))
    42
    >>> lens.set(frozendict({"x": 42}), 99)["x"]
    99
    """
    from funstruct.collections.frozendict import frozendict

    def _set(s, value):
        match s:
            case frozendict():
                return s.put(key, value)
            case dict():
                return {**s, key: value}
            case _:
                raise TypeError(f"at({key!r}): cannot set on {type(s).__name__}")

    return Lens(
        _get=lambda s: s[key],
        _set=_set,
    )


__all__ = [
    "Lens",
    "at",
]
