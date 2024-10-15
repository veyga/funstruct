import pytest
from parametrization import Parametrization as P
from funstruct.cons import CList, Cons, Nil
from funstruct.tailrec import tco, tail_call


@pytest.fixture
def nil():
    return Nil()


@pytest.fixture
def one():
    return Cons(1)


@pytest.fixture
def two_one():
    return Cons(2, Cons(1))


@pytest.fixture
def three_two_one():
    return Cons(3, Cons(2, Cons(1)))


def test_cant_create_list_type():
    with pytest.raises(TypeError):
        CList()


def test_nil_is_falsey():
    assert not Nil()


def test_cons_is_truthy():
    assert Cons(1)


def test_nil_is_a_singleton():
    assert Nil() is Nil()


def test_empty_list_equals_itself():
    assert Nil() == Nil()


def test_tail_of_single_cons_is_nil():
    assert Cons(1).tail == Nil()


def test_single_cons_equals_itself():
    assert Cons(1) == Cons(1, Nil())


def test_single_cons_equals_itself_no_nil():
    assert Cons(1) == Cons(1)


def test_cons_can_fold_left():
    subtract = lambda acc, head: acc - head
    actual = Cons(1, Cons(2)).fold_left(0, subtract)
    assert actual == -3  # 0 - 1 - 2


def test_cons_can_fold_right():
    subtract = lambda head, acc: acc - head
    actual = Cons(1, Cons(2)).fold_right(0, subtract)
    assert actual == -3  # 0 - 2 - 1


@P.autodetect_parameters()
@P.case(
    name="apply nil",
    input=[],
    expected="nil",
)
@P.case(
    name="apply 1",
    input=[1],
    expected="one",
)
@P.case(
    name="two_one",
    input=[2, 1],
    expected="two_one",
)
def test_apply(input, expected, request):
    e = request.getfixturevalue(expected)
    assert CList.new(*input) == e


@P.autodetect_parameters()
@P.case(
    name="Nil",
    input=[],
    expected="nil",
)
@P.case(
    name="single element",
    input=[1],
    expected="one",
)
@P.case(
    name="multiple elements",
    input=(2, 1),
    expected="two_one",
)
def test_from_iterable(input, expected, request):
    e = request.getfixturevalue(expected)
    assert CList.from_iterable(input) == e


@P.autodetect_parameters()
@P.case(
    name="Nil",
    input="nil",
    expected=0,
)
@P.case(
    name="single cons",
    input="one",
    expected=1,
)
@P.case(
    name="cons chain",
    input="two_one",
    expected=2,
)
def test_cons_knows_its_length(input, expected, request):
    args = request.getfixturevalue(input)
    assert len(args) == expected


def test_nil_can_prepend():
    assert Nil().prepend(1) == Cons(1)


def test_cons_can_prepend():
    assert Cons(1).prepend(2) == Cons(2, Cons(1))


@P.autodetect_parameters()
@P.case(
    name="Nil",
    input=1 << Nil(),
    expected="one",
)
@P.case(
    name="single cons",
    input=2 << Cons(1),
    expected="two_one",
)
@P.case(
    name="cons chain",
    input=2 << (1 << Nil()),
    expected="two_one",
)
def test_prepend_as_dunder(input, expected, request):
    e = request.getfixturevalue(expected)
    assert input == e


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial=Nil(),
    expected=Nil(),
)
@P.case(
    name="single cons",
    initial=Cons(1),
    expected=Cons(1),
)
@P.case(
    name="cons chain",
    initial=Cons(2, Cons(1)),
    expected=Cons(1, Cons(2)),
)
def test_reversed(initial, expected):
    assert initial.reversed() == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    drop_n=2,
    initial="nil",
    expected=Nil(),
)
@P.case(
    name="single cons",
    drop_n=2,
    initial="one",
    expected=Nil(),
)
@P.case(
    name="cons chain",
    drop_n=1,
    initial="two_one",
    expected=Cons(1),
)
def test_drop(drop_n, initial, expected, request):
    input = request.getfixturevalue(initial)
    assert input.drop(drop_n) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial="nil",
    expected=Nil(),
)
@P.case(
    name="single cons",
    initial="one",
    expected=Cons(1),
)
@P.case(
    name="cons chain, drops single element",
    initial="two_one",
    expected=Cons(1),
)
@P.case(
    name="cons chain, drops multiple elements",
    initial="three_two_one",
    expected=Cons(1),
)
def test_drop_while(initial, expected, request):
    input = request.getfixturevalue(initial)
    assert input.drop_while(lambda n: n > 1) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    input=Nil(),
    expected=[],
)
@P.case(
    name="single cons",
    input=Cons(1),
    expected=[1],
)
@P.case(
    name="cons chain",
    input=Cons(2, Cons(1)),
    expected=[2, 1],
)
def test_iter(input, expected):
    elements = []
    for n in input:
        elements.append(n)
    assert elements == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    take_n=2,
    initial=Nil(),
    expected=Nil(),
)
@P.case(
    name="single cons",
    take_n=2,
    initial=Cons(1),
    expected=Cons(1),
)
@P.case(
    name="cons chain",
    take_n=1,
    initial=Cons(3, Cons(2, Cons(1))),
    expected=Cons(3),
)
def test_take(take_n, initial, expected):
    assert initial.take(take_n) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial=Nil(),
    expected=Nil(),
)
@P.case(
    name="single cons",
    initial=Cons(2),
    expected=Cons(2),
)
@P.case(
    name="cons chain, takes single element",
    initial=Cons(2, Cons(1)),
    expected=Cons(2),
)
@P.case(
    name="cons chain, takes multiple elements",
    initial=Cons(3, Cons(2, Cons(1))),
    expected=Cons(3, Cons(2)),
)
def test_take_while(initial, expected):
    assert initial.take_while(lambda n: n > 1) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial=Nil(),
    expected=Nil(),
)
@P.case(
    name="single cons",
    initial=Cons(2),
    expected=Nil(),
)
@P.case(
    name="cons chain, single match",
    initial=Cons(4, Cons(2, Cons(1))),
    expected=Cons(1),
)
@P.case(
    name="cons chain, multple matches",
    initial=Cons(3, Cons(2, Cons(1))),
    expected=Cons(3, Cons(1)),
)
def test_filter(initial, expected):
    is_odd = lambda n: n % 2 != 0
    assert initial.filter(is_odd) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial=Nil(),
    expected=Nil(),
)
@P.case(
    name="single cons",
    initial=Cons(1),
    expected=Cons(2),
)
@P.case(
    name="cons chain",
    initial=Cons(3, Cons(2, Cons(1))),
    expected=Cons(6, Cons(4, Cons(2))),
)
def test_map(initial, expected):
    double = lambda n: n * 2
    assert initial.map(double) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    initial=Nil(),
    to_append=Nil(),
    expected="nil",
)
@P.case(
    name="cons to nil",
    initial=Nil(),
    to_append=Cons(1),
    expected="one",
)
@P.case(
    name="cons to cons",
    initial=Cons(2),
    to_append=Cons(1),
    expected="two_one",
)
def test_append(initial, to_append, expected, request):
    e = request.getfixturevalue(expected)
    assert initial.append(to_append) == e
    assert initial + to_append == e


@P.autodetect_parameters()
@P.case(
    name="Nil",
    original=Nil(),
    split_at=1,
    expected=(Nil(), Nil()),
)
@P.case(
    name="single",
    original=Cons(1),
    split_at=1,
    expected=(Cons(1), Nil()),
)
@P.case(
    name="single oob",
    original=Cons(1),
    split_at=10,
    expected=(Cons(1), Nil()),
)
@P.case(
    name="two",
    original=Cons(2, Cons(1)),
    split_at=1,
    expected=(Cons(2), Cons(1)),
)
@P.case(
    name="three",
    original=Cons(3, Cons(2, Cons(1))),
    split_at=1,
    expected=(Cons(3), Cons(2, Cons(1))),
)
def test_split_at(original, split_at, expected):
    actual = original.split_at(split_at)
    assert actual == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    original=Nil(),
    expected=(Nil(), Nil()),
)
@P.case(
    name="single odd",
    original=Cons(1),
    expected=(Nil(), Cons(1)),
)
@P.case(
    name="single even",
    original=Cons(2),
    expected=(Cons(2), Nil()),
)
@P.case(
    name="splits evens/odds",
    original=CList.from_iterable([1, 2, 3, 4]),
    expected=(Cons(2, Cons(4)), Cons(1, Cons(3))),
)
def test_partition(original, expected):
    is_even = lambda n: n % 2 == 0
    assert original.partition(is_even) == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    original=Nil(),
    expected="nil",
)
@P.case(
    name="single",
    original=CList.new(1),
    expected="one",
)
@P.case(
    name="cons to cons descending",
    original=CList.from_iterable([1, 2]),
    expected="two_one",
)
def test_sorted(original, expected, request):
    e = request.getfixturevalue(expected)
    assert original.sorted(lambda a, b: b - a) == e


@P.autodetect_parameters()
@P.case(
    name="Nil",
    input=Nil(),
    expected=Nil(),
)
@P.case(
    name="one",
    input=Cons(1),
    expected=Cons(1),
)
@P.case(
    name="two_one",
    input=Cons(2, Cons(1)),
    expected=Cons(2, Cons(1)),
)
@P.case(
    name="nested 1 level",
    input=Cons(Cons(2), Cons(Cons(1))),
    expected=Cons(2, Cons(1)),
)
@P.case(
    name="nestd 1 level, more elements",
    input=Cons(Cons(1, Cons(1)), Cons(Cons(2, Cons(2)))),
    expected=Cons.from_iterable([1, 1, 2, 2]),
)
@P.case(
    name="nested 1+ levels",
    input=CList.from_iterable(
        [Cons(5), Cons(4), CList.from_iterable([Cons(3, Cons(2))])]
    ),
    expected=CList.from_iterable([5, 4, 3, 2]),
)
def test_flatten(input, expected):
    assert input.flatten() == expected


@P.autodetect_parameters()
@P.case(
    name="Nil",
    original=Nil(),
    expected=Nil(),
)
@P.case(
    name="it maps",
    original=Cons(1),
    expected=Cons(3, Cons(3)),
)
@P.case(
    name="it maps and flattens",
    original=Cons(2, Cons(1)),
    expected=Cons.from_iterable([6, 6, 3, 3]),
)
def test_flat_map(original, expected):
    triple = lambda n: CList.from_iterable([n * 3, n * 3])
    assert original.flat_map(triple) == expected
