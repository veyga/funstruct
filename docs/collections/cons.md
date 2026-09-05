# CList (Cons List)

::: funstruct.collections.cons

## Overview

`CList` is a persistent, immutable singly-linked list. It lives in
`collections` because it's primarily used as a data structure, but it is
a full `Monad` — it supports `map`, `bind`, `ap`, `product`, and `do`.

The `+` operator on `CList` is **list concatenation** (monoid append), not
applicative `product`:

```python
Cons(1, Cons(2, Nil())) + Cons(3, Nil())  # Cons(1, Cons(2, Cons(3, Nil())))
```

### ap (function application)

`ap` applies each function in the list to each value — Cartesian product of
function application:

```python
fs = CList.from_iterable([lambda x: x + 1, lambda x: x * 10])
xs = CList.from_iterable([1, 2, 3])
fs.ap(xs)  # CList([2, 3, 4, 10, 20, 30])
```

### bind (flatMap)

```python
xs = CList.from_iterable([1, 2, 3])
xs.bind(lambda n: CList.fill(n, n))  # CList([1, 2, 2, 3, 3, 3])
```

## API Reference

::: funstruct.collections.cons.CList

::: funstruct.collections.cons.Cons

::: funstruct.collections.cons.Nil
