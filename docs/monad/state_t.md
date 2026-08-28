# StateT

A monad transformer that adds state-threading to any monad (Result, Maybe, etc.).

`StateT[S, F, A]` represents `S -> F[(S, A)]`.

```python
from funstruct.monad import StateT
from returns.result import Success, Failure


def divide_state(divisor):
    def run(s):
        if divisor == 0:
            return Failure("division by zero")
        return Success((s, s / divisor))

    return StateT(run)


result = divide_state(2).run(10)  # Success((10, 5.0))
result = divide_state(0).run(10)  # Failure("division by zero")
```

## API Reference

::: funstruct.monadtransformer.state_t.StateT
