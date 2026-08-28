"""Writer monad — computations with accumulated output.

>>> from funstruct.monad.writer import Writer
>>> from funstruct.typeclass.monoid import Monoid
>>> list_m = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])
>>> w = Writer(1, ["init"], list_m)
>>> w.map(lambda x: x + 10)
Writer(value=11, output=['init'])
>>> w.bind(lambda x: Writer(x + 1, ["inc"], list_m))
Writer(value=2, output=['init', 'inc'])
>>> Writer.pure(99, list_m)
Writer(value=99, output=[])
"""

from _funstruct._writer import Writer
from funstruct.typeclasses import Monoid
from funstruct.collections.cons import CList, Nil


class ListWriter(Writer):
    _monoid = Monoid(typ=CList, combine=lambda a, b: a + b, empty=Nil())


class StrWriter(Writer):
    _monoid = Monoid(typ=str, combine=lambda a, b: a + b, empty="")


class IntWriter(Writer):
    _monoid = Monoid(typ=int, combine=lambda a, b: a + b, empty=0)
