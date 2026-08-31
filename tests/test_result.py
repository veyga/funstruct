from funstruct.monad.result import Err, Ok, Result, Try


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
