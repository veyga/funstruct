"""Tests for Traversable — traverse and sequence on CList and Tree."""

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.collections.tree import Branch, Leaf
from funstruct.monad.either import Either, Left, Right
from funstruct.monad.option import Nothing, Option, Some


class TestCListTraverse:
    def test_traverse_all_right(self):
        xs = CList.from_iterable([1, 2, 3])
        result = xs.traverse(lambda x: Right(x * 2), Either.pure)
        assert result == Right(CList.from_iterable([2, 4, 6]))

    def test_traverse_short_circuits_on_left(self):
        xs = CList.from_iterable([1, 2, 3])
        result = xs.traverse(
            lambda x: Left("fail") if x == 2 else Right(x), Either.pure
        )
        assert result == Left("fail")

    def test_traverse_empty_list(self):
        xs = Nil()
        result = xs.traverse(lambda x: Right(x), Either.pure)
        assert result == Right(Nil())

    def test_traverse_with_option(self):
        xs = CList.from_iterable([1, 2, 3])
        result = xs.traverse(lambda x: Some(x * 10), Option.pure)
        assert result == Some(CList.from_iterable([10, 20, 30]))

    def test_traverse_option_short_circuits(self):
        xs = CList.from_iterable([1, 2, 3])
        result = xs.traverse(
            lambda x: Nothing() if x == 2 else Some(x), Option.pure
        )
        assert result == Nothing()


class TestCListSequence:
    def test_sequence_all_right(self):
        xs = CList.from_iterable([Right(1), Right(2), Right(3)])
        result = xs.sequence(Either.pure)
        assert result == Right(CList.from_iterable([1, 2, 3]))

    def test_sequence_short_circuits(self):
        xs = CList.from_iterable([Right(1), Left("err"), Right(3)])
        result = xs.sequence(Either.pure)
        assert result == Left("err")

    def test_sequence_empty(self):
        xs = Nil()
        result = xs.sequence(Either.pure)
        assert result == Right(Nil())

    def test_sequence_all_some(self):
        xs = CList.from_iterable([Some(1), Some(2)])
        result = xs.sequence(Option.pure)
        assert result == Some(CList.from_iterable([1, 2]))

    def test_sequence_with_nothing(self):
        xs = CList.from_iterable([Some(1), Nothing()])
        result = xs.sequence(Option.pure)
        assert result == Nothing()


class TestTreeTraverse:
    def test_leaf_traverse(self):
        t = Leaf(5)
        result = t.traverse(lambda x: Right(x * 2), Either.pure)
        assert result == Right(Leaf(10))

    def test_branch_traverse_all_right(self):
        t = Branch(1, Leaf(2), Leaf(3))
        result = t.traverse(lambda x: Right(x * 10), Either.pure)
        assert result == Right(Branch(10, Leaf(20), Leaf(30)))

    def test_branch_traverse_short_circuits(self):
        t = Branch(1, Leaf(2), Leaf(3))
        result = t.traverse(
            lambda x: Left("fail") if x == 2 else Right(x), Either.pure
        )
        assert result == Left("fail")

    def test_deep_tree_traverse(self):
        t = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        result = t.traverse(lambda x: Some(x + 100), Option.pure)
        assert result == Some(Branch(101, Branch(102, Leaf(103), Leaf(104)), Leaf(105)))


class TestTreeSequence:
    def test_leaf_sequence(self):
        t = Leaf(Right(42))
        result = t.sequence(Either.pure)
        assert result == Right(Leaf(42))

    def test_branch_sequence_all_right(self):
        t = Branch(Right(1), Leaf(Right(2)), Leaf(Right(3)))
        result = t.sequence(Either.pure)
        assert result == Right(Branch(1, Leaf(2), Leaf(3)))

    def test_branch_sequence_short_circuits(self):
        t = Branch(Right(1), Leaf(Left("err")), Leaf(Right(3)))
        result = t.sequence(Either.pure)
        assert result == Left("err")
