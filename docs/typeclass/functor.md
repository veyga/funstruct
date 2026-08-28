# Functor

Transform the value inside a context without changing the structure.

```
F[A] ---( f: A -> B )---> F[B]
```

```python
Valid(3).map(lambda x: x * 2)  # Valid(6)
```

## API Reference

::: funstruct.typeclasses._functor.Functor
