"""An immutable, hashable dictionary backed by a hash array mapped trie (HAMT).

This impl does not honor insertion ordering.
Nested dicts are deep-frozen by default.

Examples:
    >>> from funstruct.collections.frozendict import frozendict
    >>> fd = frozendict({"a": 1, "b": 2})
    >>> fd["a"]
    1
    >>> fd.map(lambda x: x * 10)["a"]
    10
    >>> (fd + frozendict({"c": 3}))["c"]
    3

    Nested access — dicts are deep-frozen automatically:

    >>> users = frozendict({
    ...     "alice": {"profile": {"age": 30, "city": "NYC"}},
    ...     "bob": {"profile": {"age": 25, "city": "LA"}},
    ... })
    >>> users["alice"]["profile"]["age"]
    30
    >>> users["bob"]["profile"]["city"]
    'LA'

    Map over nested values:

    >>> users.map(lambda u: u.map(lambda p: p.put("active", True)))["alice"]["profile"]["active"]
    True
"""

from __future__ import annotations

from collections.abc import Callable, ItemsView, Iterator, KeysView, ValuesView
from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.typeclasses._foldable import Foldable
from funstruct.typeclasses._functor import Functor

K = TypeVar("K")
V = TypeVar("V")
V2 = TypeVar("V2")
B = TypeVar("B")

# 5 bits per level → 32-way branching. This means:
#   - Depth is log32(n): ~6 levels for 1 billion entries
#   - Each lookup/insert traverses at most 6-7 nodes (effectively O(1))
#   - 32 is the empirical sweet spot (Bagwell/Hickey): high enough branching
#     to keep the tree shallow, small enough that path-copying on insert
#     doesn't allocate too much per node. Fits well in CPU cache lines.
_BITS = 5
_WIDTH = 1 << _BITS  # 32
_MASK = _WIDTH - 1


@dataclass(frozen=True, slots=True)
class _Empty:
    """Sentinel for empty HAMT node."""

    def get(self, key, hash_val, shift):
        return None

    def put(self, key, value, hash_val, shift):
        return _Leaf(key, value)

    def remove(self, key, hash_val, shift):
        return self

    def items_iter(self):
        return iter(())

    def __len__(self):
        return 0


@dataclass(frozen=True, slots=True)
class _Leaf:
    """Single key-value entry."""

    key: object
    value: object

    def get(self, key, hash_val, shift):
        return self.value if self.key == key else None

    def put(self, key, value, hash_val, shift):
        if self.key == key:
            return _Leaf(key, value)
        existing_hash = hash(self.key)
        if existing_hash == hash_val:
            return _Collision(hash_val, ((self.key, self.value), (key, value)))
        return _make_branch(
            self.key, self.value, existing_hash, key, value, hash_val, shift
        )

    def remove(self, key, hash_val, shift):
        if self.key == key:
            return _EMPTY
        return self

    def items_iter(self):
        yield (self.key, self.value)

    def __len__(self):
        return 1


@dataclass(frozen=True, slots=True)
class _Collision:
    """Multiple entries with the same hash."""

    hash_val: int
    entries: tuple

    def get(self, key, hash_val, shift):
        for k, v in self.entries:
            if k == key:
                return v
        return None

    def put(self, key, value, hash_val, shift):
        if hash_val != self.hash_val:
            node = _Branch(_EMPTY, 0, ())
            node = node.put(
                self.entries[0][0],
                self.entries[0][1],
                self.hash_val,
                shift,
            )
            for k, v in self.entries[1:]:
                node = node.put(k, v, self.hash_val, shift)
            return node.put(key, value, hash_val, shift)
        new_entries = tuple(
            (key, value) if k == key else (k, v) for k, v in self.entries
        )
        if all(k != key for k, _ in self.entries):
            new_entries = self.entries + ((key, value),)
        return _Collision(self.hash_val, new_entries)

    def remove(self, key, hash_val, shift):
        new_entries = tuple((k, v) for k, v in self.entries if k != key)
        if len(new_entries) == 1:
            return _Leaf(new_entries[0][0], new_entries[0][1])
        if len(new_entries) == 0:
            return _EMPTY
        return _Collision(self.hash_val, new_entries)

    def items_iter(self):
        yield from self.entries

    def __len__(self):
        return len(self.entries)


@dataclass(frozen=True, slots=True)
class _Branch:
    """Bitmap-indexed 32-way branch node."""

    _empty: _Empty
    _bitmap: int
    _children: tuple

    def get(self, key, hash_val, shift):
        idx = (hash_val >> shift) & _MASK
        bit = 1 << idx
        if not (self._bitmap & bit):
            return None
        pos = bin(self._bitmap & (bit - 1)).count("1")
        return self._children[pos].get(key, hash_val, shift + _BITS)

    def put(self, key, value, hash_val, shift):
        idx = (hash_val >> shift) & _MASK
        bit = 1 << idx
        pos = bin(self._bitmap & (bit - 1)).count("1")

        if self._bitmap & bit:
            child = self._children[pos]
            new_child = child.put(key, value, hash_val, shift + _BITS)
            new_children = (
                self._children[:pos] + (new_child,) + self._children[pos + 1 :]
            )
            return _Branch(self._empty, self._bitmap, new_children)
        else:
            new_child = _Leaf(key, value)
            new_children = self._children[:pos] + (new_child,) + self._children[pos:]
            return _Branch(self._empty, self._bitmap | bit, new_children)

    def remove(self, key, hash_val, shift):
        idx = (hash_val >> shift) & _MASK
        bit = 1 << idx
        if not (self._bitmap & bit):
            return self
        pos = bin(self._bitmap & (bit - 1)).count("1")
        child = self._children[pos]
        new_child = child.remove(key, hash_val, shift + _BITS)
        if new_child is _EMPTY:
            new_bitmap = self._bitmap ^ bit
            if new_bitmap == 0:
                return _EMPTY
            new_children = self._children[:pos] + self._children[pos + 1 :]
            match new_children:
                case (_Leaf() as leaf,):
                    return leaf
                case _:
                    return _Branch(self._empty, new_bitmap, new_children)
        new_children = self._children[:pos] + (new_child,) + self._children[pos + 1 :]
        return _Branch(self._empty, self._bitmap, new_children)

    def items_iter(self):
        for child in self._children:
            yield from child.items_iter()

    def __len__(self):
        return sum(len(c) for c in self._children)


def _make_branch(k1, v1, h1, k2, v2, h2, shift):
    """Create a branch that distinguishes two keys at the given shift."""
    idx1 = (h1 >> shift) & _MASK
    idx2 = (h2 >> shift) & _MASK
    if idx1 == idx2:
        child = _make_branch(k1, v1, h1, k2, v2, h2, shift + _BITS)
        bit = 1 << idx1
        return _Branch(_EMPTY, bit, (child,))
    bit1 = 1 << idx1
    bit2 = 1 << idx2
    if idx1 < idx2:
        children = (_Leaf(k1, v1), _Leaf(k2, v2))
    else:
        children = (_Leaf(k2, v2), _Leaf(k1, v1))
    return _Branch(_EMPTY, bit1 | bit2, children)


_EMPTY = _Empty()


class frozendict(Functor[V], Foldable, Generic[K, V]):
    """An immutable, persistent dictionary backed by a HAMT.

    Functor over values (map transforms V, keys unchanged).
    Foldable over values.
    Semigroup via combine/+ (right-biased merge).
    """

    def __init__(self, *args, shallow: bool = False, **kwargs) -> None:
        def _freeze(v):
            match v:
                case dict():
                    return frozendict(v)
                case list():
                    return [_freeze(item) for item in v]
                case _:
                    return v

        match args:
            case (frozendict() as other, *_):
                object.__setattr__(self, "_frozendict__root", other.__root)
                object.__setattr__(self, "_frozendict__size", other.__size)
            case _:
                from funstruct.util.tailrec import tail_call, tco

                source = dict(*args, **kwargs)
                items = list(source.items())

                @tco
                def _build(idx, root):
                    if idx >= len(items):
                        return root
                    k, v = items[idx]
                    return tail_call(_build)(idx + 1, root.put(k, v if shallow else _freeze(v), hash(k), 0))

                object.__setattr__(self, "_frozendict__root", _build(0, _EMPTY))
                object.__setattr__(self, "_frozendict__size", len(items))
        object.__setattr__(self, "_frozendict__hash_cache", None)

    def __setattr__(self, name, value):
        raise AttributeError("frozendict is immutable")

    def __delattr__(self, name):
        raise AttributeError("frozendict is immutable")

    def __getitem__(self, key: K) -> V:
        result = self.__root.get(key, hash(key), 0)
        if result is None and not self.__contains__(key):
            raise KeyError(key)
        return result

    def get(fa: frozendict, key: K) -> V | None:
        return fa.__root.get(key, hash(key), 0)

    def __eq__(self, other: object) -> bool:
        match other:
            case frozendict():
                if self.__size != other.__size:
                    return False
                return all(other.get(k) == v for k, v in self.items())
            case dict():
                if self.__size != len(other):
                    return False
                return all(other.get(k) == v for k, v in self.items())
            case _:
                return False

    def __contains__(self, key) -> bool:
        for k, _ in self.__root.items_iter():
            if k == key:
                return True
        return False

    def __len__(self) -> int:
        return self.__size

    def keys(self) -> KeysView[K]:
        return dict(self.items()).keys()

    def values(self) -> ValuesView[V]:
        return dict(self.items()).values()

    def items(self) -> ItemsView[K, V]:
        return dict(self.__root.items_iter()).items()

    def __iter__(self) -> Iterator[K]:
        for k, _ in self.__root.items_iter():
            yield k

    def __repr__(self) -> str:
        return f"frozendict({dict(self.__root.items_iter())})"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        if self.__hash_cache is None:
            h = 0
            for k, v in self.__root.items_iter():
                h ^= hash((k, v))
            object.__setattr__(self, "_frozendict__hash_cache", h)
        return self.__hash_cache

    def put(fa: frozendict, k: K, v: V) -> frozendict:
        new_root = fa.__root.put(k, v, hash(k), 0)
        new_fd = object.__new__(frozendict)
        new_size = fa.__size if k in fa else fa.__size + 1
        object.__setattr__(new_fd, "_frozendict__root", new_root)
        object.__setattr__(new_fd, "_frozendict__size", new_size)
        object.__setattr__(new_fd, "_frozendict__hash_cache", None)
        return new_fd

    def remove(fa: frozendict, k: K) -> frozendict:
        if k not in fa:
            return fa
        new_root = fa.__root.remove(k, hash(k), 0)
        new_fd = object.__new__(frozendict)
        object.__setattr__(new_fd, "_frozendict__root", new_root)
        object.__setattr__(new_fd, "_frozendict__size", fa.__size - 1)
        object.__setattr__(new_fd, "_frozendict__hash_cache", None)
        return new_fd

    def combine(fa: frozendict, other: frozendict) -> frozendict:
        result = fa
        for k, v in other.__root.items_iter():
            result = result.put(k, v)
        return result

    def __add__(self, other: frozendict) -> frozendict:
        """Semigroup combine (merge). Right-biased on key conflicts."""
        return self.combine(other)

    def map(fa: frozendict[K, V], f: Callable[[V], V2]) -> frozendict[K, V2]:
        root = _EMPTY
        size = 0
        for k, v in fa.__root.items_iter():
            root = root.put(k, f(v), hash(k), 0)
            size += 1
        new_fd = object.__new__(frozendict)
        object.__setattr__(new_fd, "_frozendict__root", root)
        object.__setattr__(new_fd, "_frozendict__size", size)
        object.__setattr__(new_fd, "_frozendict__hash_cache", None)
        return new_fd

    def fold_left(fa: frozendict[K, V], acc: B, f: Callable[[B, V], B]) -> B:
        for _, v in fa.__root.items_iter():
            acc = f(acc, v)
        return acc

    def fold_right(fa: frozendict[K, V], acc: B, f: Callable[[V, B], B]) -> B:
        items = list(fa.__root.items_iter())
        for _, v in reversed(items):
            acc = f(v, acc)
        return acc

    @property
    def raw(self) -> dict:
        return dict(self.__root.items_iter())

    @classmethod
    def fromkeys(cls, *args, **kwargs) -> frozendict:
        return cls(dict.fromkeys(*args, **kwargs))

    @staticmethod
    def new() -> frozendict:
        return frozendict()

    @staticmethod
    def combine_dicts(fd1: frozendict, fd2: frozendict) -> frozendict:
        return fd1.combine(fd2)

    def __bool__(self) -> bool:
        return self.__size > 0


__all__ = [
    "frozendict",
]
