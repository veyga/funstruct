# Monad

::: funstruct.typeclasses.Monad

## Do-notation

Haskell and Scala have built-in `do`/`for` syntax that flattens nested
`bind` chains into sequential-looking code. Python doesn't, but generators
give us something close.

Every monad in funstruct provides a `do` classmethod that wraps a generator
function, returning a **callable**:

```python
Monad.do(gen_fn)  # → Callable[..., Monad]
```

Call the result with `()` to execute the pipeline. Each `yield` unwraps a
monadic value (equivalent to `bind`); the final `return` is wrapped back
into the monad.

### Basic usage

Without do-notation, chaining multiple steps requires nested lambdas:

```python
from funstruct.monad.either import Either, Right, Left

result = (
    Right(1)
    .bind(lambda x: Right(x + 10)
    .bind(lambda y: Right(x + y)))
)
# Right(12)
```

With do-notation:

```python
@Either.do
def pipeline():
    x = yield Right(1)
    y = yield Right(x + 10)
    return x + y

pipeline()  # Right(12) — note the ()
```

Or called directly:

```python
Either.do(pipeline)()  # Right(12)
```

### With arguments

`do` returns a callable, so arguments are passed naturally:

```python
from funstruct.monad.option import Option, Some, Nothing

@Option.do
def lookup(user_id):
    user = yield find_user(user_id)
    email = yield get_email(user)
    return email

lookup(42)  # Some("alice@example.com") or Nothing()
```

Or without the decorator:

```python
Option.do(lookup)(42)
```

### As a decorator

`@Monad.do` wraps the generator function. The decorated name is a callable
that produces the monad when called:

```python
from funstruct.monad.state import State

inc = State(lambda s: (s + 1, s))
get = State(lambda s: (s, s))

@State.do
def count_to_three():
    a = yield inc
    b = yield inc
    c = yield inc
    total = yield get
    return (a, b, c, total)

count_to_three().run(0)  # (3, (0, 1, 2, 3))
```

### Short-circuiting

Each monad's `do` knows how to short-circuit according to its semantics:

```python
@Option.do
def pipeline():
    x = yield Some(1)
    y = yield Nothing()   # short-circuits here
    return x + y          # never reached

pipeline()  # Nothing()
```

```python
@Either.do
def pipeline():
    x = yield Right(1)
    y = yield Left("boom")   # short-circuits here
    return x + y              # never reached

pipeline()  # Left("boom")
```

### Monad transformers

Monad transformers also support do-notation. The short-circuiting respects
both layers:

```python
from funstruct.monad.either import Right
from funstruct.monad.option import Some
from funstruct.experimental.monadtransformer.either_t import EitherT

@EitherT.do
def pipeline():
    x = yield EitherT(Some(Right(1)))
    y = yield EitherT(Some(Right(x + 10)))
    return x + y

pipeline().run()  # Some(Right(12))
```

### Future and AsyncResult (async)

`Future.do` and `AsyncResult.do` use regular (sync) generators — **not
`async def`**. The driver loop handles awaiting internally. Using `async def`
with `yield` creates an async generator, which Python forbids from returning
a value.

```python
from funstruct.monad.future import Future

@Future.do
def fetch_and_transform(url):
    response = yield fetch(url)
    parsed = yield parse(response)
    return parsed.title

result = await fetch_and_transform("https://example.com")
```

`AsyncResult.do` additionally accepts sync `Either` values (Ok/Err)
alongside `AsyncResult` values:

```python
from funstruct.monad.result import AsyncResult, Ok, Err

@AsyncResult.do
def get_user_email(username):
    user = yield get_user(username)       # AsyncResult
    email = yield validate_email(user)    # can be Ok/Err or AsyncResult
    return email

result = await get_user_email("alice")  # Ok("alice@example.com")
```

### CList (the exception)

`CList.do` exists but cannot express list-monad nondeterminism. The list
monad needs to replay the generator body once per element (exploring all
combinations), but Python generators are single-use. Use explicit `.bind()`
chains instead:

```python
from funstruct.collections.cons import CList, Cons, Nil

xs = CList.from_iterable([1, 2])
ys = CList.from_iterable(["a", "b"])

result = xs.bind(lambda x: ys.map(lambda y: (x, y)))
# CList([(1, "a"), (1, "b"), (2, "a"), (2, "b")])
```
