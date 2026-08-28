"""Tests for Validated applicative"""

from parametrization import Parametrization as P

from funstruct.applicative.validated import Invalid, Valid, Validated
from funstruct.collections.cons import Cons, Nil
from funstruct.collections.frozendict import frozendict
from funstruct.typeclasses import Semigroup
from tests.laws import assert_functor_laws, assert_semigroup_laws

invalid_concat = Semigroup(typ=Invalid, combine=lambda a, b: a.ap(b))


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

    def test_product_both_valid(self):
        result = Valid(1).ap(Valid(2))
        assert result == Valid((1, 2))

    def test_product_with_invalid(self):
        result = Valid(1).ap(Invalid(["err"]))
        assert result == Invalid(["err"])


class TestInvalid:
    def test_is_valid(self):
        assert Invalid(["err"]).is_valid is False

    def test_map_is_noop(self):
        assert Invalid(["err"]).map(lambda x: x * 2) == Invalid(["err"])

    def test_product_accumulates(self):
        result = Invalid(["a"]).ap(Invalid(["b"]))
        assert result == Invalid(["a", "b"])

    def test_product_with_valid(self):
        result = Invalid(["a"]).ap(Valid(1))
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
        result = Valid(None).ap(Valid(None)).ap(Valid(None))
        assert result.is_valid

    def test_chain_accumulates_all_errors(self):
        result = Invalid(["a"]).ap(Invalid(["b"])).ap(Invalid(["c"]))
        assert result == Invalid(["a", "b", "c"])

    def test_mixed_accumulates_errors_only(self):
        result = (
            Valid(None).ap(Invalid(["first"])).ap(Valid(None)).ap(Invalid(["second"]))
        )
        assert result == Invalid(["first", "second"])


class TestValidatedCond:
    def test_real_world_validation(self):
        result = (
            Validated.cond("value" == "value", None, "bad auth")
            .ap(Validated.cond("a" in ["a", "b"], None, "no member"))
            .ap(Validated.cond(1 < 2, None, "less than"))
        )
        assert result.is_valid

    def test_real_world_multiple_failures(self):
        result = (
            Validated.cond("wrong" == "value", None, "bad auth")
            .ap(Validated.cond("unknown" in ["a", "b"], None, "no member"))
            .ap(Validated.cond(5 < 2, None, "less than"))
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
        assert result.fold(lambda errs: errs, lambda _: []) == [
            "first",
            "second",
        ]

    def test_add_is_same_as_product(self):
        a = Valid(1)
        b = Invalid(["err"])
        assert (a + b) == a.ap(b)


class TestSemigroup:
    """Validated works with any Semigroup (type with +), not just CList."""

    def test_string_semigroup(self):
        """str is a Semigroup over concatenation."""
        validated = Invalid("error1: ").ap(Invalid("error2"))
        assert validated == Invalid("error1: error2")

    def test_int_semigroup(self):
        """int is a Semigroup over addition — count errors."""
        validated = Invalid(1).ap(Invalid(1)).ap(Invalid(1))
        assert validated == Invalid(3)

    def test_int_semigroup_valid(self):
        """int is a Semigroup over addition — count errors."""
        validated = Valid(1) + Invalid(2) + Invalid(3)
        assert validated == Invalid(5)

    def test_default_uses_cons_list(self):
        """Validated.invalid() wraps in CList by default."""
        validated = Validated.invalid("a").ap(Validated.invalid("b"))
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

        validated = a(dct) + b(dct)
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
    """to_result converts Validated to Either. Valid always → Right, Invalid always → Left.

    The value's truthiness is irrelevant — Valid(0), Valid(None), Valid(False)
    all produce Right. Validation status determines the case, not the value.
    """

    def test_valid_to_result(self):
        from funstruct.monad.either import Right

        assert Valid(42).to_result() == Right(42)

    def test_valid_falsey_values_still_right(self):
        from funstruct.monad.either import Right

        assert Valid(0).to_result() == Right(0)
        assert Valid(None).to_result() == Right(None)
        assert Valid(False).to_result() == Right(False)
        assert Valid("").to_result() == Right("")
        assert Valid([]).to_result() == Right([])

    def test_invalid_to_result(self):
        from funstruct.monad.either import Left

        assert Invalid(["err"]).to_result() == Left(["err"])

    def test_valid_to_result_or(self):
        from funstruct.monad.either import Right

        assert Valid(1).to_result_or(ValueError) == Right(1)

    def test_invalid_to_result_or(self):
        from funstruct.monad.either import Left

        result = Invalid(["a", "b"]).to_result_or(ValueError)
        match result:
            case Left(e):
                assert isinstance(e, ValueError)
                assert "a; b" in str(e)

    def test_invalid_to_result_or_custom_combine(self):
        from funstruct.monad.either import Left

        result = Invalid([1, 2, 3]).to_result_or(
            TypeError, combine=lambda errs: str(sum(errs))
        )
        match result:
            case Left(e):
                assert isinstance(e, TypeError)
                assert "6" in str(e)
