# StateT

A monad transformer that adds state-threading to any monad.

`StateT[S, F, A]` represents `S -> F[(S, A)]`.

```python
from funstruct.monad import StateT, Either, Right, Left


def divide_state(divisor):
    def run(s):
        if divisor == 0:
            return Left("division by zero")
        return Right((s, s / divisor))

    return StateT(run)


result = divide_state(2).run(10)  # Right((10, 5.0))
result = divide_state(0).run(10)  # Left('division by zero')
```

## API Reference

::: funstruct.monadtransformer.state_t
