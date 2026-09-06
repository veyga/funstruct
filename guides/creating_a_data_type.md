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

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from funstruct.typeclasses import DataType

A = TypeVar("A")


class RemoteData(DataType, Generic[A]):
    """RemoteData[A] = NotAsked | Loading | Failure(error) | Success(value).

    Models the lifecycle of an async request.
    """

    @classmethod
    def pure(cls, value: A) -> RemoteData[A]:
        return Success(value)

    @property
    def is_success(self) -> bool:
        return False


class NotAsked(RemoteData):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __repr__(self): return "NotAsked()"
    def __eq__(self, other): return isinstance(other, NotAsked)
    def __bool__(self): return False


class Loading(RemoteData):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __repr__(self): return "Loading()"
    def __eq__(self, other): return isinstance(other, Loading)
    def __bool__(self): return False


@dataclass(frozen=True, eq=False)
class Failure(RemoteData[A]):
    error: Exception
    def __eq__(self, other):
        return isinstance(other, Failure) and self.error == other.error
    def __repr__(self): return f"Failure({self.error!r})"
    def __bool__(self): return False


@dataclass(frozen=True, eq=False)
class Success(RemoteData[A]):
    value: A
    @property
    def is_success(self) -> bool: return True
    def __eq__(self, other):
        return isinstance(other, Success) and self.value == other.value
    def __repr__(self): return f"Success({self.value!r})"
    def __bool__(self): return True
```

Key points:
- Extends `DataType` — gets TypeConstructor + DotNotation automatically
- `Generic[A]` — parameterized over the success value type
- Singleton variants (`NotAsked`, `Loading`) — like `Nothing`
- Frozen dataclass variants (`Failure`, `Success`) — like `Err`/`Ok`
- `pure` classmethod — creates `Success(value)`

## Step 2: Create typeclass instances

```python
from funstruct.typeclasses.monad import Monad
from funstruct.typeclasses.monad_error import MonadError


class _RemoteDataMonadError(MonadError, for_type=RemoteData):
    """MonadError instance — only implements primitives.

    map, ap, product, then, map2 are all inherited from the
    Monad → Applicative → Functor hierarchy.
    """

    def pure(self, value):
        return Success(value)

    def bind(self, fa: RemoteData, f):
        match fa:
            case Success(value):
                return f(value)
            case _:
                return fa  # NotAsked, Loading, Failure — short-circuit

    def raise_error(self, error):
        return Failure(error)

    def handle_error_with(self, fa: RemoteData, f):
        match fa:
            case Failure(error):
                return f(error)
            case _:
                return fa
```

Key points:
- Extends `MonadError` (which extends `Monad → Applicative → Functor`)
- `for_type=RemoteData` — auto-registered, no manual `register()` call
- Only implements `pure`, `bind`, `raise_error`, `handle_error_with`
- `map`, `ap`, `product`, `then`, `map2` come for free from the hierarchy

## Step 3: What you get for free

With just those two primitives (`pure` + `bind`), you get:

```python
# map — transform the success value
Success(10).map(lambda x: x * 2)           # Success(20)
NotAsked().map(lambda x: x * 2)            # NotAsked()
Loading().map(lambda x: x * 2)             # Loading()
Failure(err).map(lambda x: x * 2)          # Failure(err)

# bind — chain operations that might change state
Success(10).bind(lambda x: Success(x + 1)) # Success(11)
Success(10).bind(lambda x: Failure(err))   # Failure(err)
NotAsked().bind(lambda x: Success(99))     # NotAsked()

# >> operator (bind alias)
Success(10) >> (lambda x: Success(x + 1))  # Success(11)

# * operator (product)
Success(1) * Success(2)                    # Success((1, 2))

# ap — apply a function in context
Success(lambda x: x + 1).ap(Success(10))   # Success(11)

# handle_error_with — recover from Failure
Failure(err).handle_error_with(lambda e: Success("default"))  # Success("default")

# raise_error — create a Failure
RemoteData.raise_error(ValueError("timeout"))  # Failure(ValueError("timeout"))
```

All derived from `pure` + `bind` via the typeclass hierarchy.

## Step 4: Use with summon (tagless final)

```python
from funstruct.typeclasses import Monad, MonadError, summon

# Generic function — works with RemoteData, Result, Either, etc.
def fetch_and_transform(F: Monad, fetch_fn, transform_fn):
    return F.bind(fetch_fn(), lambda data: F.pure(transform_fn(data)))

# Use with RemoteData
F = summon(Monad, RemoteData)
result = fetch_and_transform(F, lambda: Success(42), lambda x: x * 2)
# Success(84)

# Same function with Result
from funstruct.monad.result import Result, Ok
G = summon(Monad, Result)
result = fetch_and_transform(G, lambda: Ok(42), lambda x: x * 2)
# Ok(84)
```

## Step 5: Test it

```python
import pytest
from funstruct.typeclasses import Monad, MonadError, Functor, summon

class TestRemoteDataInstances:
    def test_pure(self):
        assert RemoteData.pure(42) == Success(42)

    def test_map_success(self):
        assert Success(10).map(lambda x: x * 2) == Success(20)

    def test_map_not_asked(self):
        assert NotAsked().map(lambda x: x * 2) == NotAsked()

    def test_map_loading(self):
        assert Loading().map(lambda x: x * 2) == Loading()

    def test_bind_success(self):
        assert Success(10).bind(lambda x: Success(x + 1)) == Success(11)

    def test_bind_short_circuits(self):
        assert NotAsked().bind(lambda x: Success(99)) == NotAsked()
        assert Loading().bind(lambda x: Success(99)) == Loading()

    def test_raise_error(self):
        F = summon(MonadError, RemoteData)
        assert isinstance(F.raise_error(ValueError("x")), Failure)

    def test_handle_error_with(self):
        err = Failure(ValueError("timeout"))
        result = err.handle_error_with(lambda e: Success("cached"))
        assert result == Success("cached")

    # Dot syntax == summon equivalence
    def test_dot_equals_summon(self):
        f = lambda x: x + 1
        assert Success(10).map(f) == summon(Monad, RemoteData).map(Success(10), f)

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

## Step 6: File structure

```text
mylib/
    remote_data/
        __init__.py      # RemoteData, NotAsked, Loading, Failure, Success
        instances.py     # _RemoteDataMonadError(MonadError, for_type=RemoteData)
```

At the bottom of `__init__.py`:
```python
import mylib.remote_data.instances  # triggers auto-registration
```

## Checklist

- [ ] Data type extends `DataType` + `Generic[A]`
- [ ] Variants are frozen dataclasses (or singletons for empty cases)
- [ ] `pure` classmethod on the base type
- [ ] Instance class extends the appropriate typeclass with `for_type=`
- [ ] Only implement primitives — let the hierarchy derive the rest
- [ ] `import instances` at the bottom of `__init__.py`
- [ ] Test monad laws (left identity, right identity, associativity)
- [ ] Test dot syntax == summon equivalence
- [ ] Test short-circuit behavior for each variant
