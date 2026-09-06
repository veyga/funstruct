# What is a Monad?

A monad is a pattern for chaining operations where each step depends
on the previous result, and the context (failure, absence, state, etc.)
is handled automatically.

## The practical definition

A Monad has two operations:

- **`pure(a)`** — put a value into the context
- **`bind(fa, f)`** — take the value out, apply a function that produces a new context

That's it. Everything else (`map`, `ap`, `product`, `then`, `do`) is
derived from these two.

## A concrete example

Suppose you're building a user profile from a chain of lookups.
Each lookup might fail. Without monads:

```python
def get_profile(user_id: str) -> str | None:
    user = lookup_user(user_id)
    if user is None:
        return None

    email = get_email(user)
    if email is None:
        return None

    prefs = get_preferences(user)
    if prefs is None:
        return None

    return f"{user.name} ({email}) - theme: {prefs.theme}"
```

Every step checks for None. The happy path is buried.

With the Option monad — bind chains the operations, and Nothing
short-circuits automatically:

```python
from funstruct.monad.option import Option, Some, Nothing

def lookup_user(user_id: str) -> Option[User]:
    return Some(User("Alice")) if user_id == "1" else Nothing()

def get_email(user: User) -> Option[str]:
    return Some("alice@example.com")

def get_preferences(user: User) -> Option[Prefs]:
    return Some(Prefs(theme="dark"))

# Bind chain — each step depends on the previous result
result = (
    lookup_user("1")
    .bind(lambda user: get_email(user)
    .bind(lambda email: get_preferences(user)
    .map(lambda prefs: f"{user.name} ({email}) - theme: {prefs.theme}")))
)
# result = Some("Alice (alice@example.com) - theme: dark")

# If any step returns Nothing, everything short-circuits:
result = lookup_user("999").bind(lambda user: get_email(user))
# result = Nothing() — no error checking needed
```

## Do-notation makes it readable

The bind chain above is correct but hard to read. Do-notation
flattens it:

```python
@Option.do
def get_profile(user_id: str):
    user = yield lookup_user(user_id)
    email = yield get_email(user)
    prefs = yield get_preferences(user)
    return f"{user.name} ({email}) - theme: {prefs.theme}"

get_profile("1")    # Some("Alice (alice@example.com) - theme: dark")
get_profile("999")  # Nothing()
```

Each `yield` extracts the value from the Option. If any step returns
Nothing, the rest is skipped. The `return` value is wrapped in Some.

## The same pattern, different contexts

The power of monads: the SAME pattern works for different contexts.

**Option** — value might not exist:

```python
@Option.do
def pipeline():
    x = yield Some(10)
    y = yield Some(x + 1)
    return x + y
# Some(21)
```

**Result** — computation might fail with an error:

```python
@Result.do
def pipeline():
    x = yield Ok(10)
    y = yield Ok(x + 1)
    return x + y
# Ok(21)
```

**Either** — computation might fail with a typed error:

```python
@Either.do
def pipeline():
    x = yield Right(10)
    y = yield Right(x + 1)
    return x + y
# Right(21)
```

**State** — computation threads state:

```python
@State.do
def pipeline():
    x = yield State.get()           # read current state
    yield State.modify(lambda s: s + 1)  # modify state
    y = yield State.get()           # read again
    return (x, y)

pipeline().run(0)  # (1, (0, 1)) — state went from 0 to 1
```

Same `yield` syntax, same short-circuit behavior, different context.
That's what makes it a monad — the pattern is abstract, the context
is concrete.

## The three monad laws

Every monad must satisfy these laws (funstruct tests verify them):

**Left identity**: `pure(a).bind(f) == f(a)`

Wrapping a value and immediately binding is the same as just calling f:

```python
assert Option.pure(10).bind(lambda x: Some(x + 1)) == Some(11)
assert (lambda x: Some(x + 1))(10) == Some(11)
```

**Right identity**: `m.bind(pure) == m`

Binding with pure doesn't change anything:

```python
assert Some(10).bind(Some) == Some(10)
```

**Associativity**: `m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))`

The order of binding doesn't matter (as long as the sequence is the same):

```python
f = lambda x: Some(x + 1)
g = lambda x: Some(x * 2)
m = Some(5)

assert m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
# Both give Some(12)
```

## When to use which monad

| Monad | Context | Short-circuits on |
|-------|---------|------------------|
| `Option` | Value might not exist | `Nothing()` |
| `Result` | Computation might fail (Exception) | `Err(exception)` |
| `Either` | Computation might fail (typed error) | `Left(error)` |
| `State` | Threaded state | Never (always succeeds) |
| `Reader` | Shared environment | Never (always succeeds) |
| `Writer` | Accumulated output | Never (always succeeds) |
| `CList` | Multiple values | Never (collects all) |
| `Future`/`AsyncResult` | Async computation | `Err` (AsyncResult only) |

## See also

- `demos/01_result_pipeline.py` — AsyncResult pipeline
- `demos/02_do_notation.py` — do-notation variants
- `demos/10_writer_stacktrace.py` — Writer monad with call tracing
- `demos/11_state_counter.py` — State monad with counter, stack, interpreter
- `guides/railway_oriented_programming.md` — error handling deep dive
