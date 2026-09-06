from funstruct.monad.result import AsyncResult, Err, Ok, Result, Try
from tests.laws import assert_type_contract


class TestTypeContract:
    def test_ok_type_contract(self):
        assert_type_contract(Ok.pure, Ok)


class TestTry:
    def test_success(self):
        @Try
        def divide(a, b):
            return a / b

        assert divide(10, 2) == Ok(5.0)

    def test_failure(self):
        @Try
        def divide(a, b):
            return a / b

        result = divide(10, 0)
        assert result.is_err
        match result:
            case Err(e):
                assert type(e) is ZeroDivisionError

    def test_value_error(self):
        @Try
        def parse(s):
            return int(s)

        result = parse("abc")
        assert result.is_err
        match result:
            case Err(e):
                assert type(e) is ValueError

    def test_preserves_function_name(self):
        @Try
        def my_func():
            return 42

        assert my_func.__name__ == "my_func"


class TestDo:
    def test_success(self):
        def pipeline():
            x = yield Ok(1)
            y = yield Ok(x + 10)
            return x + y

        assert Result.do(pipeline)() == Ok(12)

    def test_short_circuits(self):
        def pipeline():
            x = yield Ok(1)
            y = yield Err(ValueError("boom"))
            return x + y

        result = Result.do(pipeline)()
        assert result.is_err

    def test_multiple_binds(self):
        def pipeline():
            a = yield Ok(1)
            b = yield Ok(2)
            c = yield Ok(3)
            return a + b + c

        assert Result.do(pipeline)() == Ok(6)


class TestFold:
    def test_ok_fold(self):
        result = Ok(42).fold(on_err=lambda e: 0, on_ok=lambda x: x * 2)
        assert result == 84

    def test_err_fold(self):
        result = Err(ValueError("bad")).fold(
            on_err=lambda e: str(e), on_ok=lambda x: x * 2
        )
        assert result == "bad"

    def test_fold_positional_err_first(self):
        ok = Ok("hello").fold(lambda e: -1, len)
        assert ok == 5

        err = Err(ValueError("x")).fold(lambda e: -1, len)
        assert err == -1


class TestAsyncResultFold:
    def test_ok_fold(self):
        import asyncio

        async def go():
            return await AsyncResult.pure(42).fold(
                on_err=lambda e: 0, on_ok=lambda x: x * 2
            )

        assert asyncio.run(go()) == 84

    def test_err_fold(self):
        import asyncio

        async def go():
            return await AsyncResult.raise_error(ValueError("bad")).fold(
                on_err=lambda e: str(e), on_ok=lambda x: x * 2
            )

        assert asyncio.run(go()) == "bad"


class TestCreatedAt:
    def test_err_captures_creation_site(self):
        from funstruct.util.created_at import CreatedAt

        err = Err(ValueError("bad"))
        assert isinstance(err.created_at, CreatedAt)
        assert err.created_at.funcname == "test_err_captures_creation_site"
        assert "test_result.py" in err.created_at.filename

    def test_err_created_at_str(self):
        err = Err(ValueError("bad"))
        s = str(err.created_at)
        assert "test_result.py" in s
        assert "test_err_created_at_str" in s


class TestConstructors:
    def test_ok_direct_equals_pure(self):
        assert Ok(42) == Ok.pure(42)

    def test_ok_direct_is_ok_type(self):
        assert type(Ok(42)) is Ok

    def test_ok_pure_is_ok_type(self):
        assert type(Ok.pure(42)) is Ok

    def test_result_pure_is_ok_type(self):
        assert type(Result.pure(42)) is Ok

    def test_result_raise_error_is_err_type(self):
        err = ValueError("bad")
        assert type(Result.raise_error(err)) is Err

    def test_result_raise_error_wraps_exception(self):
        err = ValueError("bad")
        result = Result.raise_error(err)
        match result:
            case Err(e):
                assert e is err

    def test_err_direct_vs_raise_error(self):
        err = ValueError("bad")
        assert Err(err) == Result.raise_error(err)


class TestProperties:
    def test_ok_is_ok(self):
        assert Ok(42).is_ok is True
        assert Ok(42).is_err is False

    def test_err_is_err(self):
        assert Err("bad").is_ok is False
        assert Err("bad").is_err is True

    def test_ok_repr(self):
        assert repr(Ok(42)) == "Ok(42)"

    def test_err_repr(self):
        assert repr(Err("bad")) == "Err('bad')"


class TestLeftMap:
    def test_ok_unchanged(self):
        assert Ok(42).left_map(lambda e: str(e)) == Ok(42)

    def test_err_transforms(self):
        result = Err(ValueError("bad")).left_map(lambda e: TypeError(str(e)))
        match result:
            case Err(e):
                assert type(e) is TypeError


class TestHandleErrorWith:
    def test_ok_unchanged(self):
        assert Ok(42).handle_error_with(lambda e: Ok(0)) == Ok(42)

    def test_err_recovers(self):
        result = Err(ValueError("bad")).handle_error_with(lambda e: Ok("recovered"))
        assert result == Ok("recovered")


class TestBimap:
    def test_ok_maps_right(self):
        assert Ok(5).bimap(str, lambda x: x * 2) == Ok(10)

    def test_err_maps_left(self):
        result = Err("err").bimap(str.upper, lambda x: x * 2)
        assert result == Err("ERR")


class TestGetOrElse:
    def test_ok_returns_value(self):
        assert Ok(42).get_or_else(0) == 42

    def test_err_returns_default(self):
        assert Err("bad").get_or_else(0) == 0


class TestSwap:
    def test_ok_to_err(self):
        result = Ok(42).swap()
        assert result == Err(42)

    def test_err_to_ok(self):
        result = Err("bad").swap()
        assert result == Ok("bad")


class TestResultInstances:
    """Tests exercising typeclass instances via summon (covers instances.py)."""

    def test_monad_pure(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Result).pure(42) == Ok(42)

    def test_monad_bind_ok(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Result).bind(Ok(1), lambda x: Ok(x + 1)) == Ok(2)

    def test_monad_bind_err(self):
        from funstruct.typeclasses import Monad, summon
        err = Err(ValueError("x"))
        assert summon(Monad, Result).bind(err, lambda x: Ok(x + 1)) is err

    def test_monad_map_derived(self):
        from funstruct.typeclasses import Monad, summon
        assert summon(Monad, Result).map(Ok(10), lambda x: x * 2) == Ok(20)

    def test_raise_error_via_summon(self):
        from funstruct.typeclasses import MonadError, summon
        assert isinstance(summon(MonadError, Result).raise_error(ValueError("x")), Err)

    def test_handle_error_with_err(self):
        from funstruct.typeclasses import MonadError, summon
        result = summon(MonadError, Result).handle_error_with(
            Err(ValueError("x")), lambda e: Ok("recovered")
        )
        assert result == Ok("recovered")

    def test_handle_error_with_ok_passthrough(self):
        from funstruct.typeclasses import MonadError, summon
        assert summon(MonadError, Result).handle_error_with(Ok(42), lambda e: Ok(0)) == Ok(42)

    def test_bifunctor_bimap_ok(self):
        from funstruct.typeclasses import Bifunctor, summon
        assert summon(Bifunctor, Result).bimap(Ok(10), str, lambda x: x * 2) == Ok(20)

    def test_bifunctor_bimap_err(self):
        from funstruct.typeclasses import Bifunctor, summon
        err = ValueError("bad")
        result = summon(Bifunctor, Result).bimap(Err(err), lambda e: TypeError(str(e)), lambda x: x * 2)
        assert isinstance(result, Err)

    def test_dot_vs_summon_map(self):
        from funstruct.typeclasses import Monad, summon
        f = lambda x: x + 1
        assert Ok(10).map(f) == summon(Monad, Result).map(Ok(10), f)
