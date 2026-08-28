# Validated

Applicative error-accumulating type.

Use `Validated` for combinations on validating functions.

## Example

```python
from funstruct.applicative import Validated


def validate_name(name: str):
    return Validated.cond(len(name) > 0, name, "name is empty")


def validate_age(age: int):
    return Validated.cond(age >= 0, age, "age must be non-negative")


# Both validations run — errors accumulate
result = validate_name("") + validate_age(-1)
# Invalid(errors=["name is empty", "age must be non-negative"])

# On success, values are tupled
result = validate_name("Alice") + validate_age(30)
# Valid(("Alice", 30))
```

## Constructors

```python
Validated.valid(value)  # -> Valid(value)
Validated.invalid("error")  # -> Invalid(["error"])
Validated.cond(test, val, err)  # -> Valid(val) if test else Invalid([err])
```

## Combining

```python
# product / + accumulates errors from both sides
Valid(1) + Valid(2)  # Valid((1, 2))
Valid(1) + Invalid(["oops"])  # Invalid(["oops"])
Invalid(["a"]) + Invalid(["b"])  # Invalid(["a", "b"])
```

## Converting to Result

```python
Valid(42).to_result()  # Success(42)
Invalid(["e"]).to_result()  # Failure(["e"])
```

## API Reference

::: _funstruct._validated.Validated

::: _funstruct._validated.Valid

::: _funstruct._validated.Invalid
