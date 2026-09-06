# Railway Oriented Programming

## The idea

Railway oriented programming (ROP) models computations as a track
with two rails:

```text
 ───── success rail ─────────────────────────────────────→ Ok(value)
 ───── error rail   ─────────────────────────────────────→ Err(error)
```

Each function in a pipeline either:
- Stays on the success rail (transforms the value)
- Switches to the error rail (something failed)

Once on the error rail, all subsequent steps are **skipped** — the
error propagates to the end automatically.

## Without ROP (nested error checking)

```python
def process_order(order_id: str) -> str:
    user = get_user(order_id)
    if user is None:
        return "Error: user not found"

    validated = validate_order(user)
    if validated is None:
        return "Error: invalid order"

    charged = charge_card(validated)
    if charged is None:
        return "Error: payment failed"

    return f"Order complete: {charged}"
```

Every step checks for failure. The happy path is buried in error
handling. This doesn't scale — add 10 steps and you have 10 levels
of nesting.

## With ROP (Result monad)

```python
from funstruct.monad.result import Result, Ok, Err

@Result.do
def process_order(order_id: str):
    user = yield get_user(order_id)       # Err short-circuits here
    validated = yield validate_order(user)  # ...or here
    charged = yield charge_card(validated)  # ...or here
    return f"Order complete: {charged}"
```

If any step returns `Err`, the pipeline stops immediately. The error
propagates to the caller. No nesting, no manual checks.

## The four operations

funstruct's `Result` (and `Either`, `Option`) provide four operations
that correspond to the railway metaphor:

```text
pure(a)                — put a value ON the success rail
raise_error(e)         — put a value ON the error rail
bind(f)                — continue along the success rail (or skip if on error rail)
handle_error_with(f)   — recover FROM the error rail back to success
```

### map — transform on the success rail

```python
Ok(10).map(lambda x: x * 2)     # Ok(20)
Err("bad").map(lambda x: x * 2)  # Err("bad") — skipped
```

### bind — chain operations that might fail

```python
def divide(a, b):
    if b == 0:
        return Err(ValueError("division by zero"))
    return Ok(a / b)

Ok(10).bind(lambda x: divide(x, 2))  # Ok(5.0)
Ok(10).bind(lambda x: divide(x, 0))  # Err(ValueError(...))
Err("already bad").bind(lambda x: divide(x, 2))  # Err("already bad")
```

### handle_error_with — recover from the error rail

```python
Err("timeout").handle_error_with(lambda e: Ok("cached_default"))
# Ok("cached_default")
```

### left_map — transform on the error rail (without recovering)

```python
Err("timeout").left_map(lambda e: f"FATAL: {e}")
# Err("FATAL: timeout")
```

## @Try — wrapping exception-throwing code

Python's ecosystem uses exceptions. `@Try` bridges the gap:

```python
from funstruct.monad.result import Try

@Try
def parse_int(s: str) -> int:
    return int(s)

parse_int("42")     # Ok(42)
parse_int("hello")  # Err(ValueError("invalid literal..."))
```

The exception is caught and put on the error rail. From there,
you can compose with `map`, `bind`, `handle_error_with`.

## Comparison with `returns` library

The Python `returns` library popularized ROP in Python. funstruct's
approach is similar but differs in architecture:

| | returns | funstruct |
|---|---|---|
| Result type | `Result[A, E]` | `Result[A]` (E is always Exception) |
| Either | Not separate | `Either[E, A]` (typed error, separate from Result) |
| Error creation | `Failure(e)` | `Err(e)` or `Result.raise_error(e)` |
| Pipeline | `.bind()`, `@pipeline` | `.bind()`, `@Result.do`, `>>` operator |
| Typeclass system | Protocol-based | Instance-based with summon |
| Architecture | Types inherit from typeclasses | Types are plain, instances separate |

The key difference: funstruct separates data from behavior via the
typeclass instance pattern. `Result` is plain data; `MonadError[Result]`
provides the operations. This means you can write generic functions
that work across `Result`, `Either`, and any future error-handling type.

## When to use which

| Type | Use when |
|------|----------|
| `Result[A]` | Errors are exceptions (`ValueError`, `IOError`). Most common. |
| `Either[E, A]` | Errors are typed domain values (`AuthError`, `ValidationError`). |
| `Option[A]` | Value might not exist. No error information. |
| `Validated[E, A]` | Accumulate ALL errors (form validation). Not a Monad. |

## See also

- `demos/01_result_pipeline.py` — AsyncResult pipeline
- `demos/02_do_notation.py` — do-notation variants
- `demos/transformers/03_alternative.py` — using AsyncResult everywhere
