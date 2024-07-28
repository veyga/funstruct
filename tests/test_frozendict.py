import pytest
from funstruct.frozendict import frozendict
from returns.maybe import Some, Nothing
from parametrization import Parametrization as P


@pytest.fixture
def base_dict() -> dict:
    return {"x": 1}


@pytest.fixture
def empty_fd() -> frozendict:
    return frozendict({})


@pytest.fixture
def fd_parity1(base_dict) -> frozendict:
    return frozendict(base_dict)


@pytest.fixture
def fd_parity2(base_dict) -> frozendict:
    return frozendict({**base_dict, "y": 2})


def test_constructor_copies_initial_dict(base_dict):
    dct = frozendict(base_dict)
    assert dct.raw is not base_dict


def test_getitem__unsafe_found_returns_item(fd_parity1):
    assert fd_parity1["x"] == 1


def test_getitem__unsafe_raises_keyerror(empty_fd):
    with pytest.raises(KeyError):
        empty_fd["y"]


def test_get_found__returns_item(fd_parity1):
    assert fd_parity1.get("x") == 1


def test_get__falsey_returns_item():
    assert frozendict({"x": 0}).get("x") == 0


def test_get__missing_returns_none(empty_fd):
    assert empty_fd.get("x") == None


def test_get_maybe__found_returns_some(fd_parity1):
    assert fd_parity1.get_maybe("x") == Some(1)


def test_get_maybe__found_falsey_returns_some():
    assert frozendict({"x": 0}).get_maybe("x") == Some(0)


def test_get_maybe__missing_returns_nothing(empty_fd):
    assert empty_fd.get_maybe("x") == Nothing


def test_fd_cannot_set_new_key(fd_parity1):
    with pytest.raises(TypeError):
        fd_parity1["y"] = 1
    with pytest.raises(AttributeError):
        fd_parity1.setitem("y", 1)


def test_fds_are_equal_based_on_underlying_dict(fd_parity1):
    other = frozendict({"x": 1})
    assert fd_parity1 == other


def test_fd_can_equal_mutable_dict(base_dict, fd_parity1):
    assert fd_parity1 == base_dict


def test_fd_cant_equal_dict_or_fd(fd_parity1):
    assert not fd_parity1 == set()


@P.autodetect_parameters()
@P.case(
    name="found",
    key="x",
    expected=True,
)
@P.case(
    name="missing",
    key="y",
    expected=False,
)
def test_keys_can_be_found_with_contains(key, expected, fd_parity1):
    if expected:
        assert key in fd_parity1
    else:
        assert key not in fd_parity1


@P.autodetect_parameters()
@P.case(
    name="empty",
    fixture="empty_fd",
    expected=0,
)
@P.case(
    name="fd_parity1",
    fixture="fd_parity1",
    expected=1,
)
@P.case(
    name="fd_parity2",
    fixture="fd_parity2",
    expected=2,
)
def test_fd_knows_it_length(fixture, expected, request):
    assert len(request.getfixturevalue(fixture)) == expected


def test_fd_can_get_its_keys(fd_parity2):
    keys = fd_parity2.keys()
    assert len(keys) == 2
    expected_keys = ["x", "y"]
    for k in keys:
        assert k in expected_keys


def test_fd_can_get_its_values(fd_parity2):
    values = fd_parity2.values()
    assert len(values) == 2
    expected_values = [1, 2]
    for v in values:
        assert v in expected_values


def test_fd_can_get_its_items(fd_parity2):
    items = fd_parity2.items()
    assert len(items) == 2
    expected_items = [("x", 1), ("y", 2)]
    for pair in items:
        assert pair in expected_items


def test_iter_iterates_over_keys(fd_parity2):
    keys = {k for k in fd_parity2}
    assert fd_parity2.keys() == keys


@P.autodetect_parameters()
@P.case(
    name="repr",
    fn=repr,
)
@P.case(
    name="str",
    fn=str,
)
def test_fd_as_string(fn, fd_parity1):
    expected = "frozendict({'x': 1})"
    assert fn(fd_parity1) == expected
    assert str(fd_parity1) == expected


def test_fd_hash_is_calculated_from_underlying_dict(fd_parity1, fd_parity2):
    assert hash(fd_parity1) != hash(fd_parity2)
    other_parity2 = frozendict({"y": 2, "x": 1})
    assert hash(fd_parity2) == hash(other_parity2)


def test_underlying_dict_value_can_still_be_mutable():
    fd = frozendict({"list": [1]})
    fd["list"].append(2)
    assert fd["list"] == [1, 2]


def test_empty_fd_is_falsy(empty_fd):
    assert not empty_fd


def test_non_empty_fd_is_truthy(fd_parity1):
    assert fd_parity1


def test_fd_does_not_copy_underlying_tuples():
    my_map = {"x": (1, 2)}
    fd = frozendict(my_map)
    assert fd["x"] is my_map["x"]


def test_fd_does_not_copy_underlying_sets():
    my_set = {1, 2, 3}
    fd = frozendict({"x": my_set})
    my_set.add(4)
    assert len(fd["x"]) == 4


def test_put__does_not_change_original(fd_parity1):
    initial = fd_parity1.raw
    fd_parity1.put("x", 2)
    assert fd_parity1.raw is initial


def test_put__returns_new(fd_parity1):
    initial = fd_parity1
    updated = fd_parity1.put("x", 2)
    assert updated is not initial


def test_combine_is_not_associative():
    a = frozendict({"x": 1})
    b = frozendict({"x": 2})
    combined = a.combine(b)
    assert combined is not a
    assert combined is not b
    assert combined == {"x": 2}


def test_combine_dicts_is_not_associative():
    a = frozendict({"x": 1})
    b = frozendict({"x": 2})
    combined = frozendict.combine_dicts(a, b)
    assert combined is not a
    assert combined is not b
    assert combined == {"x": 2}


def test_fd_can_be_created_from_keys():
    keys = ("x", "y")
    fd = frozendict.fromkeys(keys)
    assert "x" in fd
    assert "y" in fd
