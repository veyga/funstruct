# Do-Notation

## What is it?

Do-notation is syntactic sugar for chaining monadic operations.
Instead of nested `bind` calls, you write sequential code with `yield`:

```python
# Without do-notation — nested bind chains
result = (
    get_user(id)
    .bind(lambda user: get_email(user)
    .bind(lambda email: get_prefs(user)
    .map(lambda prefs: Profile(user, email, prefs))))
)

# With do-notation — flat, readable
@Result.do
def get_profile(id):
    user = yield get_user(id)
    email = yield get_email(user)
    prefs = yield get_prefs(user)
    return Profile(user, email, prefs)
```

Both produce identical results. Do-notation is purely sugar — it
compiles down to bind/map internally.

## How it works

`@Result.do` turns a generator function into a monadic pipeline:

1. Each `yield` extracts the value from the monad
2. If the monad is an error case (Err, Nothing, Left), short-circuit
3. The `return` value is wrapped in the success case (Ok, Some, Right)

```python
@Option.do
def pipeline():
    x = yield Some(10)       # x = 10
    y = yield Some(x + 1)    # y = 11
    return x + y              # Some(21)

pipeline()  # Some(21)
```

If any step fails:

```python
@Option.do
def pipeline():
    x = yield Some(10)       # x = 10
    y = yield Nothing()      # SHORT-CIRCUIT — rest never runs
    z = yield Some(99)       # never reached
    return x + y + z

pipeline()  # Nothing()
```

## Available on every monad

```python
@Option.do       # short-circuits on Nothing()
@Result.do       # short-circuits on Err(...)
@Either.do       # short-circuits on Left(...)
@AsyncResult.do  # short-circuits on Err(...), awaits internally
@State.do        # threads state through each step
@Reader.do       # threads context through each step
@Writer.do       # accumulates output through each step
@CList.do        # collects all values (flatMap semantics)
```

## The decorator pattern

`@Monad.do` wraps a generator function and returns a **callable**:

```python
@Result.do
def pipeline(x, y):     # arguments are passed through
    a = yield Ok(x)
    b = yield Ok(y)
    return a + b

result = pipeline(10, 20)  # Ok(30) — call the callable
```

You can also use `do` without the decorator:

```python
def my_gen(x):
    a = yield Ok(x)
    b = yield Ok(a + 1)
    return a + b

result = Result.do(my_gen)(10)  # Ok(21)
```

## With arguments

```python
@Result.do
def divide(a, b):
    if b == 0:
        yield Err(ValueError("division by zero"))
    return a / b

divide(10, 2)   # Ok(5.0)
divide(10, 0)   # Err(ValueError("division by zero"))
```

## Async do-notation

`@AsyncResult.do` works the same way but awaits each step:

```python
@AsyncResult.do
def fetch_profile(user_id):
    user = yield fetch_user(user_id)       # awaits AsyncResult
    email = yield fetch_email(user)         # awaits AsyncResult
    return Profile(user, email)

result = await fetch_profile("alice")  # Ok(Profile(...)) or Err(...)
```

**Important:** `@AsyncResult.do` uses `yield` (generators), NOT
`await`. You cannot write `async def` with `@do`:

```python
# WRONG — async def doesn't work with @do
@AsyncResult.do
async def pipeline():   # TypeError or unexpected behavior
    x = yield ...

# CORRECT — regular def with yield
@AsyncResult.do
def pipeline():
    x = yield ...
```

## Mixing sync and async

To use a sync `Result` inside `@AsyncResult.do`, lift it:

```python
@AsyncResult.do
def pipeline():
    x = yield AsyncResult.from_result(Ok(10))  # lift sync Result
    y = yield AsyncResult.pure(20)              # async value
    return x + y
```

## Performance

Do-notation is ~2x slower than raw bind chains due to Python's
generator protocol overhead:

```python
# Faster (~340ns for 3 steps)
Ok(10).bind(lambda x: Ok(x + 1)).bind(lambda y: Ok(y * 2))

# Slower (~800ns for 3 steps) but more readable
@Result.do
def pipeline():
    x = yield Ok(10)
    y = yield Ok(x + 1)
    return y * 2
```

For hot loops, prefer bind chains. For readability (3+ steps), use do.

## See also

- `demos/02_do_notation.py` — do-notation variants
- `guides/async.md` — async operations guide
- `guides/antipatterns.md` — anti-pattern #5 (do for 1-2 steps)
