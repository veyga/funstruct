"""A singly linked list.

>>> from funstruct.collections.cons import Cons, Nil
>>> xs = Cons(1, Cons(2, Cons(3, Nil())))
>>> xs.map(lambda x: x * 2)
Cons(2, Cons(4, Cons(6, Nil())))
>>> xs.filter(lambda x: x > 1)
Cons(2, Cons(3, Nil()))
>>> xs >> (lambda x: Cons(x, Cons(x, Nil())))
Cons(1, Cons(1, Cons(2, Cons(2, Cons(3, Cons(3, Nil()))))))
"""

from _funstruct._cons import *  # noqa F403
