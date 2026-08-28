# State

A pure functional state monad. Threads state through a computation without mutation.

`State[S, A]` represents a function `S -> (S, A)`.

```python
from funstruct.monad import State

increment = State(lambda s: (s + 1, s))

pipeline = increment >> (lambda a: State(lambda s: (s + 1, a + s)))

new_state, result = pipeline.run(0)
# new_state = 2, result = 1
```

## API Reference

::: _funstruct._state.State
