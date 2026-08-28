# Applicative

Combine independent computations. Extends [Functor](functor.md).

```
F[A] ─┐
       ├──> F[(A, B)]
F[B] ─┘
```

```python
Valid(1) + Valid(2)  # Valid((1, 2))
```

### Implementations

- [Validated](../applicative/validated.md)

## API Reference

::: funstruct.typeclasses._applicative.Applicative
