# Validated

::: funstruct.applicative.validated

## Overview

`Validated` is an applicative functor for **error accumulation**. Unlike
`Either` (which short-circuits on the first error), `Validated` collects
all errors independently.

`Validated` is intentionally **not a monad** — it has no `bind`. This is
what allows it to accumulate errors: each validation runs independently,
regardless of whether earlier ones failed.

### Basic usage

```python
from funstruct.applicative.validated import Validated, Valid, Invalid

# Validate conditions independently:
result = (
    Validated.cond(len(name) > 0, None, "name required")
    * Validated.cond("@" in email, None, "invalid email")
    * Validated.cond(age >= 18, None, "must be 18+")
)

# All errors collected:
# Invalid(errors=Cons('name required', Cons('invalid email', Nil())))
```

The `*` operator calls `product`, which combines `Valid` values into tuples
and accumulates `Invalid` errors.

### ap (function application)

`ap` applies a **wrapped function** to a wrapped value. On `Invalid`, it
accumulates errors from both sides:

```python
Valid(lambda x: x * 2).ap(Valid(5))          # Valid(10)
Valid(lambda x: x * 2).ap(Invalid(["err"]))  # Invalid(["err"])
Invalid(["a"]).ap(Invalid(["b"]))            # Invalid(["a", "b"])
```

### product (combine values)

`product` (aliased as `*`) combines two values into a tuple, accumulating
errors:

```python
Valid(1).product(Valid(2))          # Valid((1, 2))
Valid(1) * Valid(2)                 # Valid((1, 2))
Invalid(["a"]) * Invalid(["b"])    # Invalid(["a", "b"])
```

### Converting to Result

```python
result = (
    Validated.cond(False, None, "bad auth")
    * Validated.cond(False, None, "no access")
).to_result_or(ValueError)
# Err(ValueError("bad auth; no access"))
```

## API Reference

::: funstruct.applicative.validated.Validated

::: funstruct.applicative.validated.Valid

::: funstruct.applicative.validated.Invalid
