"""Tests for Tree functor."""

from funstruct.collections.cons import CList, Cons
from funstruct.collections.tree import Branch, Leaf


class TestLeaf:
    def test_map(self):
        assert Leaf(5).map(lambda x: x * 2) == Leaf(10)

    def test_size(self):
        assert Leaf(1).size == 1

    def test_depth(self):
        assert Leaf(1).depth == 0

    def test_fold(self):
        assert Leaf(5).fold(lambda v: v * 10, lambda v, left, right: 0) == 50

    def test_to_list(self):
        assert Leaf(42).to_list() == Cons.pure(42)

    def test_eq(self):
        assert Leaf(1) == Leaf(1)
        assert Leaf(1) != Leaf(2)

    def test_eq_with_branch(self):
        assert Leaf(1) != Branch(1, Leaf(2), Leaf(3))

    def test_eq_with_non_tree(self):
        assert Leaf(1) != 1


class TestBranch:
    def test_map(self):
        t = Branch(1, Leaf(2), Leaf(3))
        assert t.map(lambda x: x * 10) == Branch(10, Leaf(20), Leaf(30))

    def test_size(self):
        assert Branch(1, Leaf(2), Leaf(3)).size == 3

    def test_depth(self):
        assert Branch(1, Leaf(2), Leaf(3)).depth == 1
        deep = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        assert deep.depth == 2

    def test_fold(self):
        t = Branch(1, Leaf(2), Leaf(3))
        result = t.fold(lambda v: v, lambda v, left, right: v + left + right)
        assert result == 6

    def test_fold_deep(self):
        t = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        result = t.fold(lambda v: [v], lambda v, left, right: [v] + left + right)
        assert result == [1, 2, 3, 4, 5]

    def test_to_list(self):
        t = Branch(1, Leaf(2), Leaf(3))
        assert t.to_list() == CList.from_iterable([2, 1, 3])

    def test_to_list_deep(self):
        t = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        assert t.to_list() == CList.from_iterable([3, 2, 4, 1, 5])

    def test_eq(self):
        t1 = Branch(1, Leaf(2), Leaf(3))
        t2 = Branch(1, Leaf(2), Leaf(3))
        assert t1 == t2

    def test_not_eq_value(self):
        assert Branch(1, Leaf(2), Leaf(3)) != Branch(9, Leaf(2), Leaf(3))

    def test_not_eq_children(self):
        assert Branch(1, Leaf(2), Leaf(3)) != Branch(1, Leaf(9), Leaf(3))

    def test_eq_with_leaf(self):
        assert Branch(1, Leaf(2), Leaf(3)) != Leaf(1)

    def test_eq_with_non_tree(self):
        assert Branch(1, Leaf(2), Leaf(3)) != "not a tree"


class TestMapComposition:
    def test_nested_map(self):
        t = Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5))
        result = t.map(lambda x: x + 1).map(str)
        expected = Branch("2", Branch("3", Leaf("4"), Leaf("5")), Leaf("6"))
        assert result == expected
