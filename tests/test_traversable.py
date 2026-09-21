"""Tests for Traversable — traverse and sequence on CList and Tree."""

from funstruct.typeclasses import summon
from funstruct.typeclasses.applicative import Applicative
from funstruct.typeclasses.traversable import Traversable
from funstruct.types.cons import CList, Nil
from funstruct.types.either import Either, Left, Right
from funstruct.types.option import Nothing, Option, Some
from funstruct.types.tree import Branch, Leaf, Tree


class TestCListTraverse:
    def test_traverse_all_right(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = CList.from_iterable([1, 2, 3])
        result = T.traverse(xs, lambda x: Right(x * 2), G)
        assert result == Right(CList.from_iterable([2, 4, 6]))

    def test_traverse_short_circuits_on_left(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = CList.from_iterable([1, 2, 3])
        result = T.traverse(xs, lambda x: Left("fail") if x == 2 else Right(x), G)
        assert result == Left("fail")

    def test_traverse_empty_list(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = Nil()
        result = T.traverse(xs, lambda x: Right(x), G)
        assert result == Right(Nil())

    def test_traverse_with_option(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = CList.from_iterable([1, 2, 3])
        result = T.traverse(xs, lambda x: Some(x * 10), G)
        assert result == Some(CList.from_iterable([10, 20, 30]))

    def test_traverse_option_short_circuits(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = CList.from_iterable([1, 2, 3])
        result = T.traverse(xs, lambda x: Nothing() if x == 2 else Some(x), G)
        assert result == Nothing()


class TestCListSequence:
    def test_sequence_all_right(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = CList.from_iterable([Right(1), Right(2), Right(3)])
        result = T.sequence(xs, G)
        assert result == Right(CList.from_iterable([1, 2, 3]))

    def test_sequence_short_circuits(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = CList.from_iterable([Right(1), Left("err"), Right(3)])
        result = T.sequence(xs, G)
        assert result == Left("err")

    def test_sequence_empty(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Either)
        xs = Nil()
        result = T.sequence(xs, G)
        assert result == Right(Nil())

    def test_sequence_all_some(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = CList.from_iterable([Some(1), Some(2)])
        result = T.sequence(xs, G)
        assert result == Some(CList.from_iterable([1, 2]))

    def test_sequence_with_nothing(self):
        T = summon(Traversable, CList)
        G = summon(Applicative, Option)
        xs = CList.from_iterable([Some(1), Nothing()])
        result = T.sequence(xs, G)
        assert result == Nothing()


class TestTreeTraverse:
    def test_leaf_traverse(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Leaf(5)
        result = T.traverse(t, lambda x: Right(x * 2), G)
        assert result == Right(Leaf(10))

    def test_branch_traverse_all_right(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Branch(1, Leaf(2), Leaf(3))
        result = T.traverse(t, lambda x: Right(x * 10), G)
        assert result == Right(Branch(10, Leaf(20), Leaf(30)))

    def test_branch_traverse_short_circuits(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Branch(1, Leaf(2), Leaf(3))
        result = T.traverse(t, lambda x: Left("fail") if x == 2 else Right(x), G)
        assert result == Left("fail")

    def test_deep_tree_traverse(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Option)
        t = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        result = T.traverse(t, lambda x: Some(x + 100), G)
        assert result == Some(Branch(101, Branch(102, Leaf(103), Leaf(104)), Leaf(105)))


class TestTreeSequence:
    def test_leaf_sequence(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Leaf(Right(42))
        result = T.sequence(t, G)
        assert result == Right(Leaf(42))

    def test_branch_sequence_all_right(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Branch(Right(1), Leaf(Right(2)), Leaf(Right(3)))
        result = T.sequence(t, G)
        assert result == Right(Branch(1, Leaf(2), Leaf(3)))

    def test_branch_sequence_short_circuits(self):
        T = summon(Traversable, Tree)
        G = summon(Applicative, Either)
        t = Branch(Right(1), Leaf(Left("err")), Leaf(Right(3)))
        result = T.sequence(t, G)
        assert result == Left("err")
