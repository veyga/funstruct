# Generic Programming with Context Bounds

## What is a context bound?

A context bound constrains a generic function: "this works for any
type `T`, as long as `T` has a specific typeclass instance."

```scala
// Scala — T must have a JSONWrite instance
def jsonify[T: JSONWrite](item: T): String

// Haskell — a must have a Show instance
show :: Show a => a -> String

// Python/funstruct — summon enforces the bound at runtime
def jsonify(item):
    return summon(JSONWrite, type(item)).to_json_string(item)
```

The bound says: "I don't care what type `item` is — I just need
the right typeclass instance to exist."

## How it works in funstruct

### Step 1: summon resolves the instance

```python
from funstruct.typeclasses import summon

# summon(Typeclass, Type) → instance or TypeError
writer = summon(JSONWrite, str)   # → _StringJSONWrite()
writer = summon(JSONWrite, int)   # → _IntJSONWrite()
writer = summon(JSONWrite, dict)  # → TypeError: No instance of JSONWrite for dict
```

### Step 2: use the instance

```python
def jsonify(item) -> str:
    writer = summon(JSONWrite, type(item))  # resolve
    return writer.to_json_string(item)      # use
```

### Step 3: the bound is enforced

```python
jsonify("hello")  # works — JSONWrite[str] exists
jsonify(42)        # works — JSONWrite[int] exists
jsonify({})        # TypeError: No instance of JSONWrite for dict
```

The `TypeError` IS the bound enforcement. In Scala/Haskell, this
happens at compile time. In Python, it happens at runtime — but the
error message is just as clear.

## Patterns

### Single bound

```python
# Scala: def double[F[_]: Monad](fa: F[Int]): F[Int]
def double(F: Monad, fa):
    return F.map(fa, lambda x: x * 2)

double(summon(Monad, Option), Some(21))  # Some(42)
double(summon(Monad, Result), Ok(21))    # Ok(42)
```

### Multiple bounds

```python
# Scala: def show_sorted[A: Ordering: Showable](items: List[A]): List[String]
def show_sorted(items: list) -> list[str]:
    O = summon(Ordering, type(items[0]))   # bound 1: Ordering
    S = summon(Showable, type(items[0]))   # bound 2: Showable
    sorted_items = sorted(items, key=functools.cmp_to_key(O.compare))
    return [S.show(item) for item in sorted_items]
```

Both bounds must be satisfied. If either is missing, `summon` raises
`TypeError`.

### Auto-resolved bounds (tc_of)

For functions that receive a monadic value and need to resolve its
type constructor:

```python
from funstruct.typeclasses import tc_of

# tc_of(Some(42)) → Option
# tc_of(Ok(10))   → Result

def double(fa):
    F = summon(Monad, tc_of(fa))   # auto-resolve from the value
    return F.map(fa, lambda x: x * 2)

double(Some(21))  # Some(42) — auto-resolved
double(Ok(21))    # Ok(42)   — auto-resolved
```

`tc_of` reads `_type_constructor` from the value's class. No explicit
type parameter needed.

### Composition via bounds

The most powerful pattern: an instance that summons OTHER instances.

```python
class _ListJSONWrite(JSONWrite, for_type=list):
    def to_json_string(self, items: list) -> str:
        elem_writer = summon(JSONWrite, type(items[0]))  # bound on element type
        return "[" + ", ".join(elem_writer.to_json_string(i) for i in items) + "]"
```

`jsonify([1, 2, 3])` calls `_ListJSONWrite`, which summons
`_IntJSONWrite` for the elements. `jsonify(["a", "b"])` summons
`_StringJSONWrite`. The list instance doesn't know about int or str —
it delegates via the registry.

## Comparison

| | Haskell | Scala | Python/funstruct |
|---|---|---|---|
| Bound syntax | `Show a =>` | `[A: Show]` | `summon(Show, type(a))` |
| Resolution | Compile time | Compile time | Runtime |
| Error | Won't compile | Won't compile | `TypeError` at call site |
| Composition | Implicit | Implicit | Explicit via `summon` |

The mechanism is identical — a dictionary of operations looked up by
type. The difference is WHEN the lookup happens and WHO does it
(compiler vs runtime).

## When to use context bounds

**Use bounds** when your function should work for any type that has
the capability:

```python
def serialize(item):
    return summon(Serializable, type(item)).to_dict(item)
# Works for User, Address, Order — anything with Serializable
```

**Don't use bounds** when your function only ever works with one type:

```python
# Just use the type directly — no summon needed
def get_user_email(user: User) -> str:
    return user.email
```

## See also

- `guides/typeclass_pattern_json.md` — the JSON example in detail
- `guides/typeclass_pattern_ordering.md` — the Ordering example
- `demos/12_trait_bounds.py` — trait bounds with success + failure cases
- `demos/15_typeclass_pattern_json.py` — full JSON typeclass demo
