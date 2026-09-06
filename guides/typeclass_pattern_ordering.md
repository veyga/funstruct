# The Typeclass Pattern

## The four parts

Every typeclass usage has exactly four parts:

```text
1. The typeclass    — the interface (what capability exists)
2. The data type    — the thing that has the capability
3. The instance     — the implementation (how this type does it)
4. The consumer     — generic code that requires the capability
```

### Concrete example: Ordering

Suppose you want a generic `sort` function that works for any type
that can be compared.

**Part 1: The typeclass (the interface)**

```python
from abc import ABC, abstractmethod

class Ordering(ABC):
    """Typeclass for types that can be compared."""
    @abstractmethod
    def compare(self, a, b) -> int:
        """Returns negative if a < b, zero if equal, positive if a > b."""
        ...
```

This says: "there exists a concept called Ordering, and it requires
a `compare` operation." It says nothing about HOW any specific type
is compared.

**Part 2: The data type (the thing)**

```python
@dataclass(frozen=True)
class User:
    name: str
    age: int
```

This is plain data. It knows nothing about Ordering. It doesn't inherit
from Ordering. It's just a data type.

**Part 3: The instance (the implementation)**

```python
class UserByAge(Ordering, for_type=User):
    def compare(self, a: User, b: User) -> int:
        return a.age - b.age

class UserByName(Ordering, for_type=User):
    def compare(self, a: User, b: User) -> int:
        return (a.name > b.name) - (a.name < b.name)
```

This is the bridge — it says "Users can be ordered, and HERE'S HOW."
Notice there can be multiple instances for the same type. Users can
be ordered by age OR by name. The consumer decides which one to use.

**Part 4: The consumer (generic code)**

```python
def sort(items: list, O: Ordering) -> list:
    """Sort any list using any Ordering instance."""
    return sorted(items, key=functools.cmp_to_key(O.compare))

def maximum(items: list, O: Ordering):
    """Find the max of any list using any Ordering instance."""
    return max(items, key=functools.cmp_to_key(O.compare))
```

The consumer doesn't know about Users. It doesn't know about ages or
names. It just knows "I need an Ordering, and I'll use `compare`."

**Putting it together:**

```python
users = [User("Bob", 25), User("Alice", 30), User("Charlie", 20)]

sort(users, UserByAge())    # [Charlie(20), Bob(25), Alice(30)]
sort(users, UserByName())   # [Alice(30), Bob(25), Charlie(20)]
maximum(users, UserByAge()) # Alice(30)
```

Same data, same generic function, different behavior — determined by
which instance you provide.

## Why not just use Python's `__lt__`?

Python's comparison dunders (`__lt__`, `__eq__`) bake ONE ordering
into the type itself:

```python
@dataclass(order=True)
class User:
    name: str  # dataclass compares by field order — name first
    age: int
```

Now `User("Alice", 30) < User("Bob", 25)` compares by name, always.
If you want to sort by age, you need `key=lambda u: u.age` at every
call site.

With typeclasses:
- The data type has NO ordering baked in
- Multiple orderings can exist simultaneously
- Generic functions work with ANY ordering
- The caller chooses the ordering, not the type author

This is the fundamental difference between OOP (behavior on the object)
and typeclasses (behavior separate from the object, composed at use site).

## How this maps to funstruct

funstruct's built-in typeclasses follow the same four-part pattern:

| Part | Ordering example | funstruct |
|------|-----------------|-----------|
| Typeclass | `Ordering` | `Monad`, `Functor`, `MonadError` |
| Data type | `User` | `Option`, `Either`, `Result` |
| Instance | `UserByAge(Ordering)` | `_OptionMonad(Monad, for_type=Option)` |
| Consumer | `sort(items, O)` | `def pipeline(F: Monad): F.map(...)` |

The dot syntax (`Some(10).map(f)`) is sugar — it resolves the instance
via `summon` internally. The explicit style (`summon(Monad, Option).map(...)`)
makes the four parts visible.

## The split between data and functions

In OOP, data and behavior live together:

```python
class User:
    def __init__(self, name, age): ...
    def greet(self): return f"Hi, I'm {self.name}"
    def is_adult(self): return self.age >= 18
    def serialize(self): return {"name": self.name, "age": self.age}
```

In FP with typeclasses, they're separate:

```python
# Data (knows nothing about behavior)
@dataclass(frozen=True)
class User:
    name: str
    age: int

# Behavior (knows nothing about THIS User — works for any Showable)
def greet(S: Showable, user): return f"Hi, I'm {S.show(user)}"

# Multiple behaviors, same data
class UserShowFull(Showable, for_type=User):
    def show(self, u): return f"{u.name} (age {u.age})"

class UserShowShort(Showable, for_type=User):
    def show(self, u): return u.name
```

This separation means:
- Data types are simple (just fields)
- Behavior is composable (swap instances)
- Generic functions work across types (same `greet` for any `Showable`)
- You can add new behavior WITHOUT modifying the data type

This is the "expression problem" solution — add new types AND new
operations without modifying existing code.
