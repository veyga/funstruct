"""Tests for ZipList — element-wise applicative."""

from funstruct.applicative.ziplist import ZipList
from tests.laws import assert_functor_laws, assert_applicative_laws, assert_type_contract


class TestZipListLaws:
    def test_functor(self):
        assert_functor_laws(ZipList([1, 2, 3]))

    def test_applicative(self):
        assert_applicative_laws(
            pure_fn=ZipList.pure,
            fa=ZipList([1]),
            fb=ZipList([2]),
        )

    def test_type_contract(self):
        assert_type_contract(ZipList.pure, ZipList, is_monad=False)


class TestMap:
    def test_map(self):
        assert ZipList([1, 2, 3]).map(lambda x: x * 10) == ZipList([10, 20, 30])

    def test_map_empty(self):
        assert ZipList([]).map(lambda x: x + 1) == ZipList([])

    def test_map_single(self):
        assert ZipList([5]).map(str) == ZipList(["5"])


class TestAp:
    def test_ap_element_wise(self):
        fs = ZipList([lambda x: x + 1, lambda x: x * 2])
        xs = ZipList([10, 20])
        assert fs.ap(xs) == ZipList([11, 40])

    def test_ap_different_lengths(self):
        fs = ZipList([lambda x: x + 1, lambda x: x * 2, lambda x: x - 1])
        xs = ZipList([10, 20])
        assert fs.ap(xs) == ZipList([11, 40])

    def test_ap_empty(self):
        fs = ZipList([])
        xs = ZipList([1, 2, 3])
        assert fs.ap(xs) == ZipList([])

    def test_ap_single_function(self):
        fs = ZipList([lambda x: x + 100])
        xs = ZipList([1, 2, 3])
        assert fs.ap(xs) == ZipList([101])


class TestProduct:
    def test_product(self):
        assert ZipList([1, 2]).product(ZipList([3, 4])) == ZipList([(1, 3), (2, 4)])

    def test_product_operator(self):
        assert ZipList([1, 2]) * ZipList([3, 4]) == ZipList([(1, 3), (2, 4)])

    def test_product_different_lengths(self):
        assert ZipList([1, 2, 3]) * ZipList(["a"]) == ZipList([(1, "a")])


class TestContrastWithCList:
    """ZipList and CList have different ap semantics on the same data."""

    def test_clist_ap_is_cartesian(self):
        from funstruct.collections.cons import CList

        fs = CList.from_iterable([lambda x: x + 1, lambda x: x * 10])
        xs = CList.from_iterable([1, 2])
        result = fs.ap(xs).to_list()
        assert result == [2, 3, 10, 20]

    def test_ziplist_ap_is_elementwise(self):
        fs = ZipList([lambda x: x + 1, lambda x: x * 10])
        xs = ZipList([1, 2])
        result = fs.ap(xs).to_list()
        assert result == [2, 20]


class TestMisc:
    def test_len(self):
        assert len(ZipList([1, 2, 3])) == 3

    def test_iter(self):
        assert list(ZipList([1, 2, 3])) == [1, 2, 3]

    def test_repr(self):
        assert repr(ZipList([1, 2])) == "ZipList([1, 2])"

    def test_eq_with_list(self):
        assert ZipList([1, 2]) == [1, 2]

    def test_pure(self):
        assert ZipList.pure(42) == ZipList([42])
