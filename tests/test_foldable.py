"""Tests for the Foldable typeclass."""

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.collections.tree import Tree, Leaf, Branch


class TestCListFoldable:
    def test_fold_right_sum(self):
        xs = CList.from_iterable([1, 2, 3])
        assert xs.fold_right(0, lambda a, acc: a + acc) == 6

    def test_fold_left_sum(self):
        xs = CList.from_iterable([1, 2, 3])
        assert xs.fold_left(0, lambda acc, a: acc + a) == 6

    def test_length(self):
        assert CList.from_iterable([1, 2, 3]).length() == 3
        assert Nil().length() == 0

    def test_to_list(self):
        assert CList.from_iterable([1, 2, 3]).to_list() == [1, 2, 3]
        assert Nil().to_list() == []

    def test_is_empty(self):
        assert Nil().is_empty()
        assert not Cons(1).is_empty()


class TestTreeFoldable:
    def test_fold_right_sum(self):
        t = Branch(1, Leaf(2), Leaf(3))
        assert t.fold_right(0, lambda a, acc: a + acc) == 6

    def test_fold_right_leaf(self):
        assert Leaf(42).fold_right(0, lambda a, acc: a + acc) == 42

    def test_fold_right_collects_inorder(self):
        t = Branch(2, Leaf(1), Leaf(3))
        result = t.fold_right([], lambda a, acc: [a] + acc)
        assert result == [1, 2, 3]

    def test_fold_left_derived(self):
        t = Branch(1, Leaf(2), Leaf(3))
        assert t.fold_left(0, lambda acc, a: acc + a) == 6

    def test_length_derived(self):
        t = Branch(1, Leaf(2), Leaf(3))
        assert t.length() == 3
        assert Leaf(1).length() == 1

    def test_is_empty_derived(self):
        assert not Leaf(1).is_empty()
        assert not Branch(1, Leaf(2), Leaf(3)).is_empty()
