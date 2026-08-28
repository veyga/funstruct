"""An immutable, hashable dictionary (HAMT-backed, NOT insertion-ordered).

Examples:
    >>> from funstruct.collections.frozendict import frozendict
    >>> fd = frozendict({"a": 1, "b": 2})
    >>> fd.map(lambda x: x * 10).get("a")
    10
    >>> fd.map(lambda x: x * 10).get("b")
    20
    >>> (fd + frozendict({"c": 3})).get("c")
    3
    >>> fd.get("a")
    1
"""

from _funstruct._frozendict import frozendict as frozendict
