"""Tests for Validated applicative"""

from funstruct.applicative import Validated, Valid, Invalid


class TestValid:
    def test_is_valid(self):
        assert Valid(1).is_valid is True

    def test_map(self):
        assert Valid(5).map(lambda x: x * 2) == Valid(10)

    def test_product_both_valid(self):
        result = Valid(1).product(Valid(2))
        assert result == Valid((1, 2))

    def test_product_with_invalid(self):
        result = Valid(1).product(Invalid(["err"]))
        assert result == Invalid(["err"])

    def test_to_result(self):
        from returns.result import Success

        assert Valid(42).to_result() == Success(42)


class TestInvalid:
    def test_is_valid(self):
        assert Invalid(["err"]).is_valid is False

    def test_map_is_noop(self):
        assert Invalid(["err"]).map(lambda x: x * 2) == Invalid(["err"])

    def test_product_accumulates(self):
        result = Invalid(["a"]).product(Invalid(["b"]))
        assert result == Invalid(["a", "b"])

    def test_product_with_valid(self):
        result = Invalid(["a"]).product(Valid(1))
        assert result == Invalid(["a"])

    def test_left_map(self):
        result = Invalid(["a", "b"]).left_map(lambda errs: [e.upper() for e in errs])
        assert result == Invalid(["A", "B"])

    def test_to_result(self):
        from returns.result import Failure

        assert Invalid(["err"]).to_result() == Failure(["err"])


class TestValidatedConstructors:
    def test_valid(self):
        assert Validated.valid(42) == Valid(42)

    def test_invalid(self):
        assert Validated.invalid("err") == Invalid(["err"])

    def test_cond_true(self):
        assert Validated.cond(True, 1, "err") == Valid(1)

    def test_cond_false(self):
        assert Validated.cond(False, 1, "err") == Invalid(["err"])


class TestProduct:
    def test_chain_multiple_valid(self):
        result = Valid(None).product(Valid(None)).product(Valid(None))
        assert result.is_valid

    def test_chain_accumulates_all_errors(self):
        result = Invalid(["a"]).product(Invalid(["b"])).product(Invalid(["c"]))
        assert result == Invalid(["a", "b", "c"])

    def test_mixed_accumulates_errors_only(self):
        result = (
            Valid(None)
            .product(Invalid(["first"]))
            .product(Valid(None))
            .product(Invalid(["second"]))
        )
        assert result == Invalid(["first", "second"])


class TestMapN:
    def test_all_valid(self):
        result = map_n(lambda a, b, c: a + b + c, Valid(1), Valid(2), Valid(3))
        assert result == Valid(6)

    def test_any_invalid(self):
        result = map_n(lambda a, b: a + b, Valid(1), Invalid(["x"]))
        assert result == Invalid(["x"])

    def test_multiple_invalid(self):
        result = map_n(
            lambda a, b: a + b,
            Invalid(["x"]),
            Invalid(["y"]),
        )
        assert result == Invalid(["x", "y"])


class TestValidatedCond:
    def test_real_world_validation(self):
        result = (
            Validated.cond("secret" == "secret", None, "bad auth")
            .product(Validated.cond("svca" in ["svca", "svcb"], None, "bad aud"))
            .product(Validated.cond(1 < 2, None, "depth exceeded"))
        )
        assert result.is_valid

    def test_real_world_multiple_failures(self):
        result = (
            Validated.cond("wrong" == "secret", None, "bad auth")
            .product(Validated.cond("unknown" in ["svca", "svcb"], None, "bad aud"))
            .product(Validated.cond(5 < 2, None, "depth exceeded"))
        )
        assert not result.is_valid
        assert result.errors == ["bad auth", "bad aud", "depth exceeded"]
