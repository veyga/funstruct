"""Benchmarks for funstruct collections.

Run with: just bench
Compare against Python builtins to understand the cost of persistence.
"""

from funstruct.collections.cons import CList, Cons, Nil
from funstruct.collections.frozendict import frozendict

# ──────────────────────────────────────────────────────────────────────
# CList
# ──────────────────────────────────────────────────────────────────────


def _make_clist(n):
    lst = Nil()
    for i in range(n):
        lst = Cons(i, lst)
    return lst


class TestCListBenchmarks:
    def test_prepend_100(self, benchmark):
        benchmark(lambda: _make_clist(100))

    def test_prepend_1000(self, benchmark):
        benchmark(lambda: _make_clist(1000))

    def test_prepend_10000(self, benchmark):
        benchmark(lambda: _make_clist(10000))

    def test_map_100(self, benchmark):
        lst = _make_clist(100)
        benchmark(lambda: lst.map(lambda x: x + 1))

    def test_map_1000(self, benchmark):
        lst = _make_clist(1000)
        benchmark(lambda: lst.map(lambda x: x + 1))

    def test_filter_1000(self, benchmark):
        lst = _make_clist(1000)
        benchmark(lambda: lst.filter(lambda x: x % 2 == 0))

    def test_fold_left_1000(self, benchmark):
        lst = _make_clist(1000)
        benchmark(lambda: lst.fold_left(0, lambda acc, x: acc + x))

    def test_append_100(self, benchmark):
        a = _make_clist(100)
        b = _make_clist(100)
        benchmark(lambda: a.append(b))

    def test_reversed_1000(self, benchmark):
        lst = _make_clist(1000)
        benchmark(lambda: lst.reversed())

    def test_to_list_1000(self, benchmark):
        lst = _make_clist(1000)
        benchmark(lambda: lst.to_list())

    def test_from_iterable_1000(self, benchmark):
        data = list(range(1000))
        benchmark(lambda: CList.from_iterable(data))


# ──────────────────────────────────────────────────────────────────────
# frozendict (HAMT)
# ──────────────────────────────────────────────────────────────────────


def _make_fd(n):
    return frozendict({str(i): i for i in range(n)})


class TestFrozendictBenchmarks:
    def test_create_100(self, benchmark):
        benchmark(lambda: frozendict({str(i): i for i in range(100)}))

    def test_create_1000(self, benchmark):
        benchmark(lambda: frozendict({str(i): i for i in range(1000)}))

    def test_get_from_100(self, benchmark):
        fd = _make_fd(100)
        benchmark(lambda: fd.get("50"))

    def test_get_from_10000(self, benchmark):
        fd = _make_fd(10000)
        benchmark(lambda: fd.get("5000"))

    def test_put_into_100(self, benchmark):
        fd = _make_fd(100)
        benchmark(lambda: fd.put("new", 999))

    def test_put_into_10000(self, benchmark):
        fd = _make_fd(10000)
        benchmark(lambda: fd.put("new", 999))

    def test_remove_from_100(self, benchmark):
        fd = _make_fd(100)
        benchmark(lambda: fd.remove("50"))

    def test_remove_from_10000(self, benchmark):
        fd = _make_fd(10000)
        benchmark(lambda: fd.remove("5000"))

    def test_combine_100_100(self, benchmark):
        a = _make_fd(100)
        b = frozendict({str(i + 100): i for i in range(100)})
        benchmark(lambda: a.combine(b))

    def test_map_values_1000(self, benchmark):
        fd = _make_fd(1000)
        benchmark(lambda: fd.map(lambda v: v * 2))

    def test_iter_1000(self, benchmark):
        fd = _make_fd(1000)
        benchmark(lambda: list(fd.items()))


# ──────────────────────────────────────────────────────────────────────
# Comparison: CList vs Python list
# ──────────────────────────────────────────────────────────────────────


class TestPythonListComparison:
    """Compare CList against Python list for context."""

    def test_python_list_prepend_1000(self, benchmark):
        def build():
            lst = []
            for i in range(1000):
                lst = [i] + lst
            return lst

        benchmark(build)

    def test_python_list_append_1000(self, benchmark):
        def build():
            lst = []
            for i in range(1000):
                lst.append(i)
            return lst

        benchmark(build)

    def test_python_dict_create_1000(self, benchmark):
        benchmark(lambda: {str(i): i for i in range(1000)})

    def test_python_dict_get_from_10000(self, benchmark):
        d = {str(i): i for i in range(10000)}
        benchmark(lambda: d.get("5000"))
