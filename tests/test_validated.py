"""Tests for Validated applicative"""

from funstruct.applicative.validated import Invalid, Valid, Validated


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

    def test_fold(self):
        result = Invalid(["a", "b"]).fold(
            on_invalid=lambda errs: [e.upper() for e in errs],
            on_valid=lambda _: [],
        )
        assert result == ["A", "B"]

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


class TestValidatedCond:
    def test_real_world_validation(self):
        result = (
            Validated.cond("value" == "value", None, "bad auth")
            .product(Validated.cond("a" in ["a", "b"], None, "no member"))
            .product(Validated.cond(1 < 2, None, "less than"))
        )
        assert result.is_valid

    def test_real_world_multiple_failures(self):
        result = (
            Validated.cond("wrong" == "value", None, "bad auth")
            .product(Validated.cond("unknown" in ["a", "b"], None, "no member"))
            .product(Validated.cond(5 < 2, None, "less than"))
        )
        assert not result.is_valid
        assert result.fold(lambda errs: errs, lambda _: []) == [
            "bad auth",
            "no member",
            "less than",
        ]

    def test_real_world_multiple_failures_add(self):
        result = (
            Validated.cond("wrong" == "value", None, "bad auth")
            + Validated.cond("unknown" in ["a", "b"], None, "no member")
            + Validated.cond(5 < 2, None, "less than")
        )
        assert not result.is_valid
        assert result.fold(lambda errs: errs, lambda _: []) == [
            "bad auth",
            "no member",
            "less than",
        ]


class TestAddOperator:
    def test_valid_plus_valid(self):
        result = Valid(1) + Valid(2)
        assert result == Valid((1, 2))

    def test_valid_plus_invalid(self):
        result = Valid(1) + Invalid(["err"])
        assert result == Invalid(["err"])

    def test_invalid_plus_valid(self):
        result = Invalid(["err"]) + Valid(1)
        assert result == Invalid(["err"])

    def test_invalid_plus_invalid_accumulates(self):
        result = Invalid(["a"]) + Invalid(["b"])
        assert result == Invalid(["a", "b"])

    def test_chain_three_valids(self):
        result = Valid(1) + Valid(2) + Valid(3)
        assert result.is_valid

    def test_chain_accumulates_all_errors(self):
        result = Invalid(["a"]) + Invalid(["b"]) + Invalid(["c"])
        assert result == Invalid(["a", "b", "c"])

    def test_cond_chain_with_add(self):
        result = Validated.cond(True, None, "x") + Validated.cond(True, None, "y")
        assert result.is_valid

    def test_cond_chain_failures_with_add(self):
        result = Validated.cond(False, None, "first") + Validated.cond(
            False, None, "second"
        )
        assert result.fold(lambda errs: errs, lambda _: []) == ["first", "second"]

    def test_add_is_same_as_product(self):
        a = Valid(1)
        b = Invalid(["err"])
        assert (a + b) == a.product(b)
