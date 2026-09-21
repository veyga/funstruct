# Creating Your Own Data Type

This guide walks through creating a complete funstruct-compatible
data type from scratch: the ADT, typeclass instances, tests, and usage.

## The example: RemoteData

`RemoteData[A]` models the state of an async request — common in
UIs and API clients:

```text
RemoteData[A] = NotAsked | Loading | Failure(error) | Success(value)
```

Four states, one type. This is useful because it distinguishes
"haven't asked yet" from "asked and failed" from "asked and waiting."

## Step 1: Define the data type

Data types extend `DataType` and use `@variant` (or `@final` + `@dataclass`)
for sealed variants. Data types are **pure data** — no typeclass operations.
All behavior comes from typeclass instances.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, final

from funstruct.typeclasses import DataType

A = TypeVar("A")


class RemoteData(DataType, ABC, Generic[A]):
    """RemoteData[A] = NotAsked | Loading | Failure(error) | Success(value)."""

    @property
    @abstractmethod
    def is_success(self) -> bool: ...


@final
class NotAsked(RemoteData):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@final
class Loading(RemoteData):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@final
@dataclass(frozen=True, eq=False, repr=False)
class Failure(RemoteData[A]):
    error: Exception

    @property
    def is_success(self) -> bool: return False


@final
@dataclass(frozen=True, eq=False, repr=False)
class Success(RemoteData[A]):
    value: A

    @property
    def is_success(self) -> bool: return True
```

Key points:
- Extends `DataType` + `ABC` — gets HKTMeta + DotNotation, can't instantiate base
- `@final` on all variants — sealed, no subclassing (like Scala sealed traits)
- `@dataclass(frozen=True, eq=False, repr=False)` — immutable, no auto `__eq__`/`__repr__`
- NO typeclass operations on the type — no `bind`, `map`, `pure`, `__eq__`, `__repr__`
- DataType delegates `__eq__`, `__repr__`, `__str__`, `__bool__` to typeclass instances

## Step 2: Create typeclass instances

Each typeclass gets its own file under `instances/`:

```text
remote_data/
    __init__.py
    instances/
        __init__.py          # imports all submodules
        monad_error.py       # MonadError instance
        eq.py                # Eq instance
        representable.py     # Representable instance (__repr__)
        truthable.py         # Truthable instance (__bool__)
```

### instances/monad_error.py

```python
from funstruct.typeclasses.monad_error import MonadError

class _RemoteDataMonadError(MonadError, for_type=RemoteData):
    def pure(self, value):
        return Success(value)

    def bind(self, fa, f):
        match fa:
            case Success(value): return f(value)
            case _: return fa

    def raise_error(self, error):
        return Failure(error)

    def handle_error_with(self, fa, f):
        match fa:
            case Failure(error): return f(error)
            case _: return fa
```

### instances/eq.py

```python
from funstruct.typeclasses.eq import Eq

class _RemoteDataEq(Eq, for_type=RemoteData):
    def eq(self, a, b) -> bool:
        match a, b:
            case NotAsked(), NotAsked(): return True
            case Loading(), Loading(): return True
            case Failure(e1), Failure(e2): return e1 == e2
            case Success(v1), Success(v2): return v1 == v2
            case _: return False
```

### instances/representable.py

```python
from funstruct.typeclasses.representable import Representable

class _RemoteDataRepresentable(Representable, for_type=RemoteData):
    def represent(self, a) -> str:
        match a:
            case NotAsked(): return "NotAsked()"
            case Loading(): return "Loading()"
            case Failure(e): return f"Failure({e!r})"
            case Success(v): return f"Success({v!r})"
```

### instances/truthable.py

```python
from funstruct.typeclasses.truthable import Truthable

class _RemoteDataTruthable(Truthable, for_type=RemoteData):
    def is_truthy(self, a) -> bool:
        match a:
            case Success(): return True
            case _: return False
```

### instances/__init__.py

```python
import mylib.remote_data.instances.monad_error  # noqa: F401
import mylib.remote_data.instances.eq  # noqa: F401
import mylib.remote_data.instances.representable  # noqa: F401
import mylib.remote_data.instances.truthable  # noqa: F401
```

At the bottom of the main `__init__.py`:
```python
import mylib.remote_data.instances  # triggers auto-registration
```

## Step 3: What you get for free

With `pure` + `bind` implemented, the Monad hierarchy derives everything else:

```python
# map — derived from bind + pure
Success(10).map(lambda x: x * 2)           # Success(20)
NotAsked().map(lambda x: x * 2)            # NotAsked()

# >> operator — bind alias (from DotNotation)
Success(10) >> (lambda x: Success(x + 1))  # Success(11)

# * operator — product (from DotNotation)
Success(1) * Success(2)                    # Success((1, 2))

# ap, map2, then, do — all derived from bind + pure

# Class-level dispatch via HKTMeta:
RemoteData.pure(42)                        # Success(42)
RemoteData.raise_error(ValueError("x"))    # Failure(ValueError("x"))
RemoteData.do(gen_fn)                      # do-notation

# Python dunders via typeclass instances:
Success(1) == Success(1)                   # True (Eq)
repr(Success(42))                          # "Success(42)" (Representable)
bool(NotAsked())                           # False (Truthable)
```

## Step 4: Use with summon (tagless final)

```python
from funstruct.typeclasses import Monad, MonadError, summon

def fetch_and_transform(M: Monad, fetch_fn, transform_fn):
    return M.bind(fetch_fn(), lambda data: M.pure(transform_fn(data)))

# Works with RemoteData
M = summon(Monad, RemoteData)
result = fetch_and_transform(M, lambda: Success(42), lambda x: x * 2)
# Success(84)

# Same function with Result
from funstruct.types.result import Result, Ok
M = summon(Monad, Result)
result = fetch_and_transform(M, lambda: Ok(42), lambda x: x * 2)
# Ok(84)
```

## Step 5: Test it

```python
from funstruct.typeclasses import Monad, MonadError, summon

class TestRemoteData:
    def test_pure(self):
        assert RemoteData.pure(42) == Success(42)

    def test_map_success(self):
        assert Success(10).map(lambda x: x * 2) == Success(20)

    def test_map_not_asked(self):
        assert NotAsked().map(lambda x: x * 2) == NotAsked()

    def test_bind_short_circuits(self):
        assert NotAsked().bind(lambda x: Success(99)) == NotAsked()

    def test_repr(self):
        assert repr(Success(42)) == "Success(42)"

    def test_truthiness(self):
        assert bool(Success(1)) is True
        assert bool(NotAsked()) is False

    def test_dot_equals_summon(self):
        f = lambda x: x + 1
        M = summon(Monad, RemoteData)
        assert Success(10).map(f) == M.map(Success(10), f)

    # Monad laws
    def test_left_identity(self):
        f = lambda x: Success(x + 1)
        assert RemoteData.pure(10).bind(f) == f(10)

    def test_right_identity(self):
        m = Success(10)
        assert m.bind(Success) == m

    def test_associativity(self):
        f = lambda x: Success(x + 1)
        g = lambda x: Success(x * 2)
        m = Success(5)
        assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
```

## Checklist

- [ ] Data type extends `DataType` + `ABC` + `Generic[A]`
- [ ] `@final` on all variants — sealed
- [ ] `@dataclass(frozen=True, eq=False, repr=False)` for data-carrying variants
- [ ] Singleton pattern for empty variants (NotAsked, Loading)
- [ ] NO typeclass ops on data types — no `bind`, `map`, `__eq__`, `__repr__`, `__bool__`
- [ ] Instance per typeclass in `instances/` directory:
    - `monad_error.py` — `pure`, `bind`, `raise_error`, `handle_error_with`
    - `eq.py` — `eq` (pattern matching)
    - `representable.py` — `represent` (pattern matching)
    - `truthable.py` — `is_truthy` (pattern matching)
- [ ] `instances/__init__.py` imports all submodules
- [ ] `__init__.py` imports instances at the bottom
- [ ] Test monad laws, dot-equals-summon equivalence, short-circuit behavior
