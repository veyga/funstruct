"""Tests for Tree functor."""

from parametrization import Parametrization as P

from funstruct.collections.cons import CList, Cons
from funstruct.collections.tree import Branch, Leaf, Tree
from funstruct.typeclasses import Functor, summon
from funstruct.typeclasses.foldable import Foldable


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


# ── Instance tests via summon ────────────────────────────────────────


class TestTreeFunctorInstance:
    @P.autodetect_parameters()
    @P.case(
        name="leaf",
        tree=Leaf(42),
        f=lambda x: x + 1,
        expected=Leaf(43),
    )
    @P.case(
        name="branch",
        tree=Branch(1, Leaf(2), Leaf(3)),
        f=lambda x: x * 10,
        expected=Branch(10, Leaf(20), Leaf(30)),
    )
    @P.case(
        name="deep_branch",
        tree=Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5)),
        f=lambda x: x * 2,
        expected=Branch(2, Branch(4, Leaf(6), Leaf(8)), Leaf(10)),
    )
    def test_map_via_summon(self, tree, f, expected):
        assert summon(Functor, Tree).map(tree, f) == expected

    def test_map_dot_vs_summon(self):
        t = Branch(1, Leaf(2), Leaf(3))
        f = lambda x: x * 10
        assert t.map(f) == summon(Functor, Tree).map(t, f)


class TestTreeFoldableInstance:
    @P.autodetect_parameters()
    @P.case(
        name="leaf_sum",
        tree=Leaf(42),
        acc=0,
        expected=42,
    )
    @P.case(
        name="branch_sum",
        tree=Branch(1, Leaf(2), Leaf(3)),
        acc=0,
        expected=6,
    )
    @P.case(
        name="deep_branch_sum",
        tree=Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5)),
        acc=0,
        expected=15,
    )
    def test_fold_left_via_summon(self, tree, acc, expected):
        T = summon(Foldable, Tree)
        assert T.fold_left(tree, acc, lambda a, b: a + b) == expected

    @P.autodetect_parameters()
    @P.case(
        name="leaf_collect",
        tree=Leaf(42),
        expected=[42],
    )
    @P.case(
        name="branch_collect",
        tree=Branch(1, Leaf(2), Leaf(3)),
        expected=[2, 1, 3],
    )
    @P.case(
        name="deep_branch_collect",
        tree=Branch(1, Branch(2, Leaf(3), Leaf(4)), Leaf(5)),
        expected=[3, 2, 4, 1, 5],
    )
    def test_fold_right_via_summon(self, tree, expected):
        T = summon(Foldable, Tree)
        assert T.fold_right(tree, [], lambda x, acc: [x] + acc) == expected

    def test_fold_left_string_concat(self):
        T = summon(Foldable, Tree)
        t = Branch("a", Leaf("b"), Leaf("c"))
        result = T.fold_left(t, "", lambda acc, x: acc + x)
        assert set(result) == {"a", "b", "c"}
        assert len(result) == 3
