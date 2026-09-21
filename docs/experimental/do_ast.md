# AST-based Do-Notation (Experimental)

`funstruct.experimental.do_ast` compiles `yield` statements into
`bind`/`map` chains at decoration time via AST transformation.

## Why?

The standard `@do` uses Python generators. CList's `bind` calls the
continuation multiple times (once per element), but generators are
single-use — so `@CList.do` produces incorrect results.

The AST-based `do_ast` rewrites the function at decoration time.
No generator runs at call time — the result is nested `bind`/`map` calls.
This works for ALL monads including CList.

## Usage

```python
from funstruct.experimental.do_ast import do_ast
from funstruct.types.cons import CList

@do_ast
def cartesian():
    x = yield CList.from_iterable([1, 2])
    y = yield CList.from_iterable(["a", "b"])
    return (x, y)

cartesian()
# CList([(1, "a"), (1, "b"), (2, "a"), (2, "b")])
```

## How it works

```python
# What you write:
@do_ast
def pipeline():
    x = yield Ok(10)
    y = yield Ok(x + 1)
    return x + y

# What gets compiled (at decoration time):
def pipeline():
    def _cont_1(x):
        def _cont_2(y):
            return x + y
        return Ok(x + 1).map(_cont_2)
    return Ok(10).bind(_cont_1)
```

Each `x = yield expr` becomes `expr.bind(lambda x: ...)` using nested
named functions. Plain statements (if/else, print, assignments) between
yields are preserved in the continuation functions.

## Limitations

- Requires source code access (`inspect.getsource`) — won't work in REPL
- Yields inside control flow (`if`/`for`/`while`) fall back to the generator
- `yield` is used as a syntactic marker, not as a real generator yield

## API Reference

::: funstruct.experimental.do_ast
