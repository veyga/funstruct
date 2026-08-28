"""Option monad — presence or absence of a value.

Examples:
    >>> from funstruct.monad.option import Option, Some, Nothing
    >>> from funstruct.collections.cons import Cons, Nil, CList
    >>> Some(1).map(lambda x: x + 10)
    Some(11)
    >>> Nothing().bind(lambda x: Some(x * 2))
    Nothing()
    >>> Some(1) >> (lambda x: Some(x + 1))
    Some(2)
    >>> Option.from_optional(None)
    Nothing()

    map2 — combine two Options with a function:

    >>> Some(2).map2(Some(3), lambda a, b: a + b)
    Some(5)
    >>> Some(2).map2(Nothing(), lambda a, b: a + b)
    Nothing()

    sequence — CList[Option[A]] → Option[CList[A]]:

    >>> Option.sequence(Cons(Some(1), Cons(Some(2), Cons(Some(3), Nil()))))
    Some(Cons(1, Cons(2, Cons(3, Nil()))))
    >>> Option.sequence(Cons(Some(1), Cons(Nothing(), Cons(Some(3), Nil()))))
    Nothing()

    traverse — map then sequence:

    >>> Option.traverse(CList.from_iterable([1, 2, 3]), lambda x: Some(x * 10))
    Some(Cons(10, Cons(20, Cons(30, Nil()))))
    >>> Option.traverse(CList.from_iterable([1, 0, 3]), lambda x: Some(x) if x != 0 else Nothing())
    Nothing()
"""

from _funstruct._option import *  # noqa F403
