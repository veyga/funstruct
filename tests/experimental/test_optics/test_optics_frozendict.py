from funstruct.collections.frozendict import frozendict
from funstruct.experimental.optics import Lens, at


class TestAt:
    def test_get_from_frozendict(self):
        fd = frozendict({"x": 42})
        assert at("x").get(fd) == 42

    def test_set_on_frozendict(self):
        fd = frozendict({"x": 42})
        assert at("x").set(fd, 99)["x"] == 99

    def test_set_preserves_other_keys(self):
        fd = frozendict({"x": 1, "y": 2})
        result = at("x").set(fd, 99)
        assert result["x"] == 99
        assert result["y"] == 2

    def test_modify_on_frozendict(self):
        fd = frozendict({"x": 10})
        assert at("x").modify(fd, lambda v: v * 2)["x"] == 20

    def test_original_unchanged(self):
        fd = frozendict({"x": 1})
        at("x").set(fd, 99)
        assert fd["x"] == 1


class TestComposition:
    def test_two_level_get(self):
        fd = frozendict({"a": {"b": 1}})
        lens = at("a") >> at("b")
        assert lens.get(fd) == 1

    def test_two_level_set(self):
        fd = frozendict({"a": {"b": 1}})
        lens = at("a") >> at("b")
        result = lens.set(fd, 99)
        assert result["a"]["b"] == 99

    def test_three_level_get(self):
        fd = frozendict({"x": {"y": {"z": 42}}})
        lens = at("x") >> at("y") >> at("z")
        assert lens.get(fd) == 42

    def test_three_level_set(self):
        fd = frozendict({"x": {"y": {"z": 42}}})
        lens = at("x") >> at("y") >> at("z")
        result = lens.set(fd, 0)
        assert result["x"]["y"]["z"] == 0

    def test_three_level_modify(self):
        fd = frozendict({"x": {"y": {"z": 42}}})
        lens = at("x") >> at("y") >> at("z")
        result = lens.modify(fd, lambda v: v + 1)
        assert result["x"]["y"]["z"] == 43

    def test_set_preserves_siblings(self):
        fd = frozendict(
            {
                "alice": {"age": 30, "city": "NYC"},
                "bob": {"age": 25, "city": "LA"},
            }
        )
        lens = at("alice") >> at("age")
        result = lens.set(fd, 31)
        assert result["alice"]["age"] == 31
        assert result["alice"]["city"] == "NYC"
        assert result["bob"]["age"] == 25

    def test_original_unchanged_after_deep_set(self):
        fd = frozendict({"a": {"b": {"c": 1}}})
        lens = at("a") >> at("b") >> at("c")
        lens.set(fd, 999)
        assert fd["a"]["b"]["c"] == 1


class TestRealisticExample:
    def test_user_profile_update(self):
        """Simulate updating a user profile in a deeply nested config."""
        config = frozendict(
            {
                "app": {
                    "users": {
                        "alice": {"email": "alice@old.com", "role": "admin"},
                        "bob": {"email": "bob@example.com", "role": "user"},
                    },
                    "settings": {"theme": "dark", "version": 2},
                },
            }
        )

        email_lens = at("app") >> at("users") >> at("alice") >> at("email")
        assert email_lens.get(config) == "alice@old.com"

        updated = email_lens.set(config, "alice@new.com")
        assert updated["app"]["users"]["alice"]["email"] == "alice@new.com"
        assert updated["app"]["users"]["bob"]["email"] == "bob@example.com"
        assert updated["app"]["settings"]["theme"] == "dark"

        version_lens = at("app") >> at("settings") >> at("version")
        bumped = version_lens.modify(updated, lambda v: v + 1)
        assert bumped["app"]["settings"]["version"] == 3
        assert bumped["app"]["users"]["alice"]["email"] == "alice@new.com"
