"""An immutable, hashable dictionary.

>>> from funstruct.collections.frozendict import frozendict
>>> fd = frozendict({"a": 1, "b": 2})
>>> fd.map(lambda x: x * 10)
frozendict({'a': 10, 'b': 20})
>>> fd + frozendict({"c": 3})
frozendict({'a': 1, 'b': 2, 'c': 3})
>>> fd.get("a")
1
"""

from _funstruct._frozendict import *  # noqa F403
