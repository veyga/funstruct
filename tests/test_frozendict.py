import pytest
from parametrization import Parametrization as P

from funstruct.collections.frozendict import frozendict
from funstruct.typeclasses import Monoid
from tests.laws import (
    assert_functor_laws,
    assert_monoid_laws,
    assert_semigroup_laws,
)

FrozenDictMerge = Monoid(typ=frozendict, combine=lambda a, b: a + b, empty=frozendict())


class TestFrozendictLaws:
    def test_semigroup(self):
        assert_semigroup_laws(
            frozendict({"a": 1}),
            frozendict({"b": 2}),
            frozendict({"c": 3}),
            sg=FrozenDictMerge,
        )

    def test_monoid(self):
        assert_monoid_laws(frozendict({"a": 1, "b": 2}), sg=FrozenDictMerge)

    def test_functor(self):
        assert_functor_laws(frozendict({"x": 1, "y": 2}))


@P.autodetect_parameters()
@P.case(
    name="double values",
    fd=frozendict({"a": 1, "b": 2}),
    f=lambda x: x * 2,
    expected=frozendict({"a": 2, "b": 4}),
)
@P.case(
    name="to string",
    fd=frozendict({"x": 10, "y": 20}),
    f=str,
    expected=frozendict({"x": "10", "y": "20"}),
)
@P.case(
    name="empty",
    fd=frozendict(),
    f=lambda x: x + 1,
    expected=frozendict(),
)
@P.case(
    name="nested map",
    fd=frozendict({"a": frozendict({"inner": 1}), "b": frozendict({"inner": 2})}),
    f=lambda d: d.map(lambda v: v + 100),
    expected=frozendict(
        {"a": frozendict({"inner": 101}), "b": frozendict({"inner": 102})}
    ),
)
def test_map(fd, f, expected):
    assert fd.map(f) == expected


@P.autodetect_parameters()
@P.case(
    name="disjoint keys",
    a=frozendict({"x": 1}),
    b=frozendict({"y": 2}),
    expected=frozendict({"x": 1, "y": 2}),
)
@P.case(
    name="overlapping keys right-biased",
    a=frozendict({"x": 1, "y": 2}),
    b=frozendict({"y": 99, "z": 3}),
    expected=frozendict({"x": 1, "y": 99, "z": 3}),
)
@P.case(
    name="empty left",
    a=frozendict(),
    b=frozendict({"a": 1}),
    expected=frozendict({"a": 1}),
)
@P.case(
    name="empty right",
    a=frozendict({"a": 1}),
    b=frozendict(),
    expected=frozendict({"a": 1}),
)
def test_add(a, b, expected):
    assert a + b == expected


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
    assert empty_fd.get("x") is None


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
    assert fd_parity1.raw == initial


def test_put__returns_new(fd_parity1):
    initial = fd_parity1
    updated = fd_parity1.put("x", 2)
    assert updated is not initial


def test_combine_returns_new_instance():
    a = frozendict({"x": 1})
    b = frozendict({"x": 2})
    combined = a.combine(b)
    assert combined is not a
    assert combined is not b
    assert combined == {"x": 2}


def test_combine_dicts_returns_new_instance():
    a = frozendict({"x": 1})
    b = frozendict({"x": 2})
    combined = frozendict.combine_dicts(a, b)
    assert combined is not a
    assert combined is not b
    assert combined == {"x": 2}


def test_semigroup_associativity_with_overlapping_keys():
    """Associativity holds even with key conflicts.

    a = {x:1, y:10}
    b = {x:2, z:20}
    c = {y:3, z:30}

    Left:   (a + b) + c
            {x:2, y:10, z:20} + {y:3, z:30}
            = {x:2, y:3, z:30}

    Right:  a + (b + c)
            {x:1, y:10} + {x:2, y:3, z:30}
            = {x:2, y:3, z:30}

    Left == Right
    """
    a = frozendict({"x": 1, "y": 10})
    b = frozendict({"x": 2, "z": 20})
    c = frozendict({"y": 3, "z": 30})
    assert (a + b) + c == a + (b + c)


def test_not_commutative():
    """Merge is NOT commutative (rightmost wins on conflict).

    a = {x:1}
    b = {x:2}

    a + b = {x:2}   (b's value wins)
    b + a = {x:1}   (a's value wins)

    a + b != b + a
    """
    a = frozendict({"x": 1})
    b = frozendict({"x": 2})
    assert a + b != b + a


def test_fd_can_be_created_from_keys():
    keys = ("x", "y")
    fd = frozendict.fromkeys(keys)
    assert "x" in fd
    assert "y" in fd


# --- Coverage tests for HAMT internals ---


class CollidingKey:
    """Key that forces hash collisions for testing HAMT collision paths."""

    def __init__(self, value, hash_val=42):
        self.value = value
        self._hash = hash_val

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return isinstance(other, CollidingKey) and self.value == other.value

    def __repr__(self):
        return f"CK({self.value})"


def test_hash_collision_put():
    """Two keys with same hash go into a Collision node."""
    k1 = CollidingKey("a")
    k2 = CollidingKey("b")
    fd = frozendict({}).put(k1, 1).put(k2, 2)
    assert fd.get(k1) == 1
    assert fd.get(k2) == 2
    assert len(fd) == 2


def test_hash_collision_update():
    """Updating a key in a collision node."""
    k1 = CollidingKey("a")
    k2 = CollidingKey("b")
    fd = frozendict({}).put(k1, 1).put(k2, 2).put(k1, 10)
    assert fd.get(k1) == 10
    assert fd.get(k2) == 2
    assert len(fd) == 2


def test_hash_collision_get_missing():
    """Getting a missing key from collision node returns None."""
    k1 = CollidingKey("a")
    k2 = CollidingKey("b")
    k3 = CollidingKey("c")
    fd = frozendict({}).put(k1, 1).put(k2, 2)
    assert fd.get(k3) is None


def test_hash_collision_remove_to_leaf():
    """Removing from collision with 2 entries collapses to leaf."""
    k1 = CollidingKey("a")
    k2 = CollidingKey("b")
    fd = frozendict({}).put(k1, 1).put(k2, 2)
    fd2 = frozendict(fd.raw)
    # Rebuild without k1 by creating fresh
    items = {k: v for k, v in fd2.items() if k != k1}
    fd3 = frozendict(items)
    assert fd3.get(k2) == 2
    assert fd3.get(k1) is None


def test_hash_collision_add_third():
    """Adding a third colliding key extends the collision."""
    k1 = CollidingKey("a")
    k2 = CollidingKey("b")
    k3 = CollidingKey("c")
    fd = frozendict({}).put(k1, 1).put(k2, 2).put(k3, 3)
    assert fd.get(k1) == 1
    assert fd.get(k2) == 2
    assert fd.get(k3) == 3
    assert len(fd) == 3


def test_collision_then_different_hash():
    """Adding a key with different hash to collision promotes to branch."""
    k1 = CollidingKey("a", hash_val=42)
    k2 = CollidingKey("b", hash_val=42)
    k3 = CollidingKey("c", hash_val=99)
    fd = frozendict({}).put(k1, 1).put(k2, 2).put(k3, 3)
    assert fd.get(k1) == 1
    assert fd.get(k2) == 2
    assert fd.get(k3) == 3


def test_remove_key_from_frozendict():
    """Removing keys uses the HAMT remove path."""
    fd = frozendict({"a": 1, "b": 2, "c": 3})
    raw = {k: v for k, v in fd.items() if k != "b"}
    fd2 = frozendict(raw)
    assert fd2.get("a") == 1
    assert fd2.get("b") is None
    assert fd2.get("c") == 3


def test_init_from_frozendict():
    """frozendict can be created from another frozendict."""
    fd1 = frozendict({"a": 1, "b": 2})
    fd2 = frozendict(fd1)
    assert fd2.get("a") == 1
    assert fd2.get("b") == 2
    assert fd2 == fd1


def test_contains_on_empty():
    assert "x" not in frozendict({})


def test_setattr_raises():
    """frozendict is immutable."""
    fd = frozendict({"a": 1})
    import pytest

    with pytest.raises(AttributeError):
        fd.x = 42


def test_delattr_raises():
    fd = frozendict({"a": 1})
    import pytest

    with pytest.raises(AttributeError):
        del fd.x


def test_many_keys_exercises_branch_paths():
    """Many keys exercise deep HAMT branch/remove paths."""
    fd = frozendict({})
    for i in range(100):
        fd = fd.put(f"key_{i}", i)
    assert len(fd) == 100
    for i in range(100):
        assert fd.get(f"key_{i}") == i


class TestRemove:
    """Test key removal from frozendict."""

    def test_remove_existing_key(self):
        fd = frozendict({"a": 1, "b": 2, "c": 3})
        result = fd.remove("b")
        assert result.get("a") == 1
        assert result.get("b") is None
        assert result.get("c") == 3
        assert len(result) == 2

    def test_remove_absent_key(self):
        fd = frozendict({"a": 1})
        result = fd.remove("z")
        assert result is fd

    def test_remove_last_key(self):
        fd = frozendict({"a": 1})
        result = fd.remove("a")
        assert len(result) == 0
        assert not result

    def test_remove_preserves_original(self):
        fd = frozendict({"a": 1, "b": 2})
        fd.remove("a")
        assert fd.get("a") == 1

    def test_remove_many_keys(self):
        fd = frozendict({str(i): i for i in range(20)})
        for i in range(0, 20, 2):
            fd = fd.remove(str(i))
        assert len(fd) == 10
        for i in range(20):
            if i % 2 == 0:
                assert fd.get(str(i)) is None
            else:
                assert fd.get(str(i)) == i


class TestHashCollisions:
    """Test HAMT behavior with hash collisions."""

    def test_collision_put_and_get(self):
        class BadHash:
            def __init__(self, val):
                self.val = val

            def __hash__(self):
                return 42

            def __eq__(self, other):
                return isinstance(other, BadHash) and self.val == other.val

        k1, k2, k3 = BadHash("a"), BadHash("b"), BadHash("c")
        fd = frozendict()
        fd = fd.put(k1, 1).put(k2, 2).put(k3, 3)
        assert fd.get(k1) == 1
        assert fd.get(k2) == 2
        assert fd.get(k3) == 3
        assert len(fd) == 3

    def test_collision_overwrite(self):
        class BadHash:
            def __init__(self, val):
                self.val = val

            def __hash__(self):
                return 42

            def __eq__(self, other):
                return isinstance(other, BadHash) and self.val == other.val

        k1 = BadHash("a")
        fd = frozendict().put(k1, 1).put(k1, 99)
        assert fd.get(k1) == 99
        assert len(fd) == 1

    def test_collision_remove(self):
        class BadHash:
            def __init__(self, val):
                self.val = val

            def __hash__(self):
                return 42

            def __eq__(self, other):
                return isinstance(other, BadHash) and self.val == other.val

        k1, k2, k3 = BadHash("a"), BadHash("b"), BadHash("c")
        fd = frozendict().put(k1, 1).put(k2, 2).put(k3, 3)

        fd2 = fd.remove(k2)
        assert fd2.get(k1) == 1
        assert fd2.get(k2) is None
        assert fd2.get(k3) == 3
        assert len(fd2) == 2

    def test_collision_remove_to_leaf(self):
        class BadHash:
            def __init__(self, val):
                self.val = val

            def __hash__(self):
                return 42

            def __eq__(self, other):
                return isinstance(other, BadHash) and self.val == other.val

        k1, k2 = BadHash("a"), BadHash("b")
        fd = frozendict().put(k1, 1).put(k2, 2)
        fd2 = fd.remove(k1)
        assert fd2.get(k2) == 2
        assert len(fd2) == 1


class TestBranchRemove:
    """Test removal that causes branch collapse."""

    def test_remove_collapses_branch_to_leaf(self):
        fd = frozendict({"a": 1, "b": 2})
        fd2 = fd.remove("a")
        assert fd2.get("b") == 2
        assert len(fd2) == 1

    def test_remove_all_keys(self):
        fd = frozendict({"x": 1, "y": 2, "z": 3})
        fd = fd.remove("x").remove("y").remove("z")
        assert len(fd) == 0

    def test_remove_from_deep_branch(self):
        fd = frozendict({str(i): i for i in range(50)})
        fd2 = fd.remove("25")
        assert fd2.get("25") is None
        assert fd2.get("24") == 24
        assert len(fd2) == 49
