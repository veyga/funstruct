"""Writer monad — computations with accumulated output.

>>> from funstruct.monad.writer import ListWriter
>>> w = ListWriter(1, ["init"])
>>> w.map(lambda x: x + 10)
ListWriter(value=11, output=['init'])
>>> w.bind(lambda x: ListWriter(x + 1, ["inc"]))
ListWriter(value=2, output=['init', 'inc'])
>>> ListWriter.pure(99)
ListWriter(value=99, output=[])
"""

from _funstruct._writer import Writer
from funstruct.collections.cons import CList, Nil
from funstruct.typeclasses import Monoid


class ListWriter(Writer):
    _monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])


class CListWriter(Writer):
    _monoid = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())


class StrWriter(Writer):
    _monoid = Monoid(typ=str, combine=lambda a, b: a + b, empty="")


class IntWriter(Writer):
    _monoid = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
