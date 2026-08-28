"""Immutable binary tree — a Functor.

Tree[A] = Leaf(value) | Branch(value, left, right)

Every node holds a value. map applies a function to all values,
preserving structure. Tree is a Functor but not a Monad.

Examples:
    >>> from funstruct.collections.tree import Tree, Leaf, Branch
    >>> from funstruct.collections.cons import Cons, Nil
    >>> t = Branch(1, Leaf(2), Leaf(3))
    >>> t.map(lambda x: x * 10)
    Branch(10, Leaf(20), Leaf(30))

    >>> t.size
    3
    >>> t.depth
    1

    >>> big = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
    >>> big.map(str)
    Branch('1', Branch('2', Leaf('3'), Leaf('4')), Leaf('5'))
    >>> big.to_list()
    Cons(3, Cons(2, Cons(4, Cons(1, Cons(5, Nil())))))
    >>> big.depth
    2

    fold — reduce the tree:

    >>> t.fold(lambda v: v, lambda v, l, r: v + l + r)
    6
"""

from _funstruct._tree import Branch as Branch
from _funstruct._tree import Leaf as Leaf
from _funstruct._tree import Tree as Tree
