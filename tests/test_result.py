from funstruct.monad.result import Err, Ok, Result, Try
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
        assert result.is_left
        match result:
            case Err(e):
                assert type(e) is ZeroDivisionError

    def test_value_error(self):
        @Try
        def parse(s):
            return int(s)

        result = parse("abc")
        assert result.is_left
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
        assert result.is_left

    def test_multiple_binds(self):
        def pipeline():
            a = yield Ok(1)
            b = yield Ok(2)
            c = yield Ok(3)
            return a + b + c

        assert Result.do(pipeline)() == Ok(6)


class TestConstructors:
    def test_ok_direct_equals_pure(self):
        assert Ok(42) == Ok.pure(42)

    def test_ok_direct_is_ok_type(self):
        assert type(Ok(42)) is Ok

    def test_ok_pure_is_ok_type(self):
        assert type(Ok.pure(42)) is Ok

    def test_result_pure_is_ok_type(self):
        assert type(Result.pure(42)) is Ok

    def test_result_from_exception_is_err_type(self):
        err = ValueError("bad")
        assert type(Result.from_exception(err)) is Err

    def test_result_from_exception_wraps_exception(self):
        err = ValueError("bad")
        result = Result.from_exception(err)
        match result:
            case Err(e):
                assert e is err

    def test_err_direct_vs_from_exception(self):
        err = ValueError("bad")
        assert Err(err) == Result.from_exception(err)


class TestAliases:
    def test_ok_extends_right(self):
        from funstruct.monad.either import Right

        assert issubclass(Ok, Right)

    def test_err_extends_left(self):
        from funstruct.monad.either import Left

        assert issubclass(Err, Left)

    def test_result_extends_either(self):
        from funstruct.monad.either import Either

        assert issubclass(Result, Either)

    def test_ok_repr(self):
        assert repr(Ok(42)) == "Ok(42)"

    def test_err_repr(self):
        assert repr(Err("bad")) == "Err('bad')"
