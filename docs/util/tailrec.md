# tailrec

Trampoline-based tail recursion for Python. Eliminates stack overflow on deep recursion
by converting tail-recursive functions into iterative loops.

## Example

```python
from funstruct.tailrec import tco, tail_call


@tco
def sum_up_to(n, acc=0):
    if n == 0:
        return acc
    return tail_call(sum_up_to)(n - 1, acc + n)


sum_up_to(10000)  # no stack overflow
```

## API Reference

::: _funstruct._tailrec
