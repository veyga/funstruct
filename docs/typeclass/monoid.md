# Monoid

A [Semigroup](semigroup.md) with an identity element (`empty`).

**Law:** `empty + a == a == a + empty`

```python
# list is a monoid (empty = [])
[] + [1, 2]  # [1, 2]
```

## API Reference

::: funstruct.typeclass.monoid.Monoid
