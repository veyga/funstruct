# ReaderT

A monad transformer that adds dependency injection (environment reading) to any monad.

`ReaderT[R, F, A]` represents `R -> F[A]`.

```python
from funstruct.monad import ReaderT
from returns.result import Success

fetch_url = ReaderT(lambda config: Success(config["base_url"]))

result = fetch_url({"base_url": "https://api.example.com"})
# Success("https://api.example.com")
```

## API Reference

::: _funstruct._reader_t.ReaderT
