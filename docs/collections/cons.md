# Cons

An immutable, persistent singly-linked list. Constructed by prepending elements.

Ideal for recursive algorithms where you build lists by cons'ing onto the head.

## Example

```python
from funstruct.collections import Cons, Nil

# Build a list
xs = Cons(1, Cons(2, Cons(3, Nil)))

# Pattern match / destructure
head, tail = xs.head, xs.tail  # 1, Cons(2, Cons(3, Nil))

# Map over elements
doubled = xs.map(lambda x: x * 2)  # Cons(2, Cons(4, Cons(6, Nil)))

# Bind (flatMap) — duplicate each element
xs >> (lambda x: Cons(x, Cons(x, Nil())))
# Cons(1, Cons(1, Cons(2, Cons(2, Cons(3, Cons(3, Nil))))))
```

## Chaining operations

```python
from funstruct.collections import Cons, CList, Nil

nums = Cons(1, Cons(2, Cons(3, Cons(4, Cons(5, Nil())))))

# Pipeline: square → keep evens → duplicate each
result = (
    nums.map(lambda x: x * x).filter(  # Cons(1, 4, 9, 16, 25)
        lambda x: x % 2 == 0
    )  # Cons(4, 16)
    >> (lambda x: Cons(x, Cons(-x, Nil())))  # Cons(4, -4, 16, -16)
)

# Fold to sum
total = nums.fold_left(0, lambda acc, x: acc + x)  # 15

# Pattern matching
match nums:
    case Cons(head, tail):
        print(f"first: {head}")  # first: 1
    case Nil():
        print("empty")

# Build from Python iterable
from_list = CList.from_iterable([10, 20, 30])
# Cons(10, Cons(20, Cons(30, Nil)))

# Prepend with <<
99 << nums  # Cons(99, Cons(1, Cons(2, ...)))
```

## Common operations

```python
from funstruct.collections import Cons, Nil

xs = Cons(1, Cons(2, Cons(3, Nil())))

# Reverse
xs.reversed()  # Cons(3, Cons(2, Cons(1, Nil)))

# Append another list
xs + Cons(4, Cons(5, Nil()))
# Cons(1, Cons(2, Cons(3, Cons(4, Cons(5, Nil)))))

# Prepend an element
0 << xs  # Cons(0, Cons(1, Cons(2, Cons(3, Nil))))

# Insert at position
left, right = xs.split_at(2)  # (Cons(1, Cons(2, Nil)), Cons(3, Nil))
left + (99 << right)  # Cons(1, Cons(2, Cons(99, Cons(3, Nil))))

# Take / Drop
xs.take(2)  # Cons(1, Cons(2, Nil))
xs.drop(2)  # Cons(3, Nil)

# Sorted (with comparator)
Cons(3, Cons(1, Cons(2, Nil()))).sorted(lambda a, b: a - b)
# Cons(1, Cons(2, Cons(3, Nil)))
```

## API Reference

::: _funstruct._cons.CList

::: _funstruct._cons.Cons

::: _funstruct._cons.Nil
