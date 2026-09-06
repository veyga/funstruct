"""Tests for Validated applicative"""

from parametrization import Parametrization as P

from funstruct.applicative.validated import Invalid, Valid, Validated
from funstruct.collections.cons import Cons, Nil
from funstruct.collections.frozendict import frozendict
from funstruct.typeclasses import Semigroup
from tests.laws import assert_functor_laws, assert_semigroup_laws

invalid_concat = Semigroup(typ=Invalid, combine=lambda a, b: a.product(b))


class TestValidatedLaws:
    def test_semigroup_invalid(self):
        assert_semigroup_laws(
            Invalid(Cons("a", Nil())),
            Invalid(Cons("b", Nil())),
            Invalid(Cons("c", Nil())),
            sg=invalid_concat,
        )

    def test_functor_valid(self):
        assert_functor_laws(Valid(1))

    def test_functor_invalid(self):
        assert_functor_laws(Invalid(Cons("err", Nil())))


class TestValid:
    def test_is_valid(self):
        assert Valid(1).is_valid is True

    def test_map(self):
        assert Valid(5).map(lambda x: x * 2) == Valid(10)

    def test_ap(self):
        result = Valid(lambda x: x + 1).ap(Valid(2))
        assert result == Valid(3)

    def test_ap_with_invalid(self):
        result = Valid(lambda x: x + 1).ap(Invalid(["err"]))
        assert result == Invalid(["err"])

    def test_product_both_valid(self):
        result = Valid(1).product(Valid(2))
        assert result == Valid((1, 2))

    def test_product_with_invalid(self):
        result = Valid(1).product(Invalid(["err"]))
        assert result == Invalid(["err"])


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

    def test_real_world_multiple_failures_mul(self):
        result = (
            Validated.cond("wrong" == "value", None, "bad auth")
            * Validated.cond("unknown" in ["a", "b"], None, "no member")
            * Validated.cond(5 < 2, None, "less than")
        )
        assert not result.is_valid
        assert result.fold(lambda errs: errs, lambda _: []) == [
            "bad auth",
            "no member",
            "less than",
        ]


class TestMulOperator:
    def test_valid_mul_valid(self):
        result = Valid(1) * Valid(2)
        assert result == Valid((1, 2))

    def test_valid_mul_invalid(self):
        result = Valid(1) * Invalid(["err"])
        assert result == Invalid(["err"])

    def test_invalid_mul_valid(self):
        result = Invalid(["err"]) * Valid(1)
        assert result == Invalid(["err"])

    def test_invalid_mul_invalid_accumulates(self):
        result = Invalid(["a"]) * Invalid(["b"])
        assert result == Invalid(["a", "b"])

    def test_chain_three_valids(self):
        result = Valid(1) * Valid(2) * Valid(3)
        assert result.is_valid

    def test_chain_accumulates_all_errors(self):
        result = Invalid(["a"]) * Invalid(["b"]) * Invalid(["c"])
        assert result == Invalid(["a", "b", "c"])

    def test_cond_chain_with_mul(self):
        result = Validated.cond(True, None, "x") * Validated.cond(True, None, "y")
        assert result.is_valid

    def test_cond_chain_failures_with_mul(self):
        result = Validated.cond(False, None, "first") * Validated.cond(
            False, None, "second"
        )
        assert result.fold(lambda errs: errs, lambda _: []) == [
            "first",
            "second",
        ]

    def test_mul_is_same_as_product(self):
        a = Valid(1)
        b = Invalid(["err"])
        assert (a * b) == a.product(b)


class TestSemigroup:
    """Validated works with any Semigroup (type with +), not just CList."""

    def test_string_semigroup(self):
        """str is a Semigroup over concatenation."""
        validated = Invalid("error1: ").product(Invalid("error2"))
        assert validated == Invalid("error1: error2")

    def test_int_semigroup(self):
        """int is a Semigroup over addition — count errors."""
        validated = Invalid(1).product(Invalid(1)).product(Invalid(1))
        assert validated == Invalid(3)

    def test_int_semigroup_valid(self):
        """int is a Semigroup over addition — count errors."""
        validated = Valid(1) * Invalid(2) * Invalid(3)
        assert validated == Invalid(5)

    def test_default_uses_cons_list(self):
        """Validated.invalid() wraps in CList by default."""
        validated = Validated.invalid("a").product(Validated.invalid("b"))
        assert validated.fold(
            on_invalid=lambda errs: errs == ["a", "b"],
            on_valid=lambda _: False,
        )

    @P.autodetect_parameters()
    @P.case(
        name="both OK",
        dct=frozendict({"a": "a", "b": "b"}),
        invalids=Nil(),
    )
    @P.case(
        name="a wrong",
        dct=frozendict({"a": "A", "b": "b"}),
        invalids=Cons.pure("a wrong"),
    )
    @P.case(
        name="b wrong",
        dct=frozendict({"a": "a", "b": "B"}),
        invalids=Cons.pure("b wrong"),
    )
    @P.case(
        name="both wrong",
        dct=frozendict({"a": "A", "b": "B"}),
        invalids=["a wrong", "b wrong"],
    )
    def test_implicit_semigroup_on_cond(self, dct, invalids):
        def a(dct: dict):
            return Validated.cond(
                dct.get("a") == "a",
                None,
                "a wrong",
            )

        def b(dct: dict):
            return Validated.cond(
                dct.get("b") == "b",
                None,
                "b wrong",
            )

        validated = a(dct) * b(dct)
        if invalids:
            assert validated.fold(
                on_invalid=lambda errs: errs == invalids,
                on_valid=lambda _: False,
            )
        else:
            assert validated.fold(
                on_invalid=lambda _: False,
                on_valid=lambda _: True,
            )


class TestTruthiness:
    def test_valid_is_truthy(self):
        assert bool(Valid(1)) is True
        assert bool(Valid(None)) is True

    def test_invalid_is_falsy(self):
        assert bool(Invalid(Cons("err", Nil()))) is False


class TestToResult:
    """to_result converts Validated to Result. Valid → Ok, Invalid → Err.

    The value's truthiness is irrelevant — Valid(0), Valid(None), Valid(False)
    all produce Ok. Validation status determines the case, not the value.
    """

    def test_valid_fold_to_ok(self):
        from funstruct.monad.result import Ok, Err

        assert Valid(42).fold(Err, Ok) == Ok(42)

    def test_valid_fold_is_ok(self):
        from funstruct.monad.result import Ok, Err

        result = Valid(42).fold(Err, Ok)
        assert type(result) is Ok

    def test_valid_falsey_values_still_ok(self):
        from funstruct.monad.result import Ok, Err

        assert Valid(0).fold(Err, Ok) == Ok(0)
        assert Valid(None).fold(Err, Ok) == Ok(None)
        assert Valid(False).fold(Err, Ok) == Ok(False)
        assert Valid("").fold(Err, Ok) == Ok("")
        assert Valid([]).fold(Err, Ok) == Ok([])

    def test_invalid_fold_to_err(self):
        from funstruct.monad.result import Err, Ok

        assert Invalid(["err"]).fold(Err, Ok) == Err(["err"])

    def test_invalid_fold_is_err(self):
        from funstruct.monad.result import Err, Ok

        result = Invalid(["err"]).fold(Err, Ok)
        assert type(result) is Err

    def test_valid_fold_then_left_map(self):
        from funstruct.monad.result import Ok, Err

        result = Valid(1).fold(Err, Ok).left_map(lambda errs: ValueError(str(errs)))
        assert result == Ok(1)

    def test_invalid_fold_then_left_map(self):
        from funstruct.monad.result import Err, Ok

        result = (
            Invalid(["a", "b"])
            .fold(Err, Ok)
            .left_map(lambda errs: ValueError("; ".join(str(e) for e in errs)))
        )
        assert type(result) is Err
        match result:
            case Err(e):
                assert type(e) is ValueError
                assert "a; b" in str(e)

    def test_invalid_fold_then_left_map_custom(self):
        from funstruct.monad.result import Err, Ok

        result = (
            Invalid([1, 2, 3])
            .fold(Err, Ok)
            .left_map(lambda errs: TypeError(str(sum(errs))))
        )
        assert type(result) is Err
        match result:
            case Err(e):
                assert type(e) is TypeError
                assert "6" in str(e)

    def test_invalid_fold_left_map_pattern_match(self):
        """Err pattern-matches in case statements — the mint test scenario."""
        from funstruct.monad.result import Err, Ok

        result = (
            (
                Validated.cond(False, None, "bad auth")
                * Validated.cond(False, None, "no access")
            )
            .fold(Err, Ok)
            .left_map(lambda errs: ValueError("; ".join(str(e) for e in errs)))
        )

        match result:
            case Err(ValueError()):
                pass
            case other:
                raise AssertionError(f"Expected Err(ValueError), got {other}")
