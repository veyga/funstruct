# frozendict

An immutable, hashable dictionary. Can be used as a dict key or in sets.

## Example

```python
from funstruct.collections import frozendict

fd = frozendict({"a": 1, "b": 2})

# Immutable — returns new instances
fd2 = fd.set("c", 3)  # frozendict({"a": 1, "b": 2, "c": 3})

# Hashable — can be used in sets or as dict keys
{fd, fd2}
```

## API Reference

::: \_funstruct.\_frozendict.frozendict
