from funstruct.monad.result import Result, Ok, Err, Try


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
    def test_ok_is_right(self):
        from funstruct.monad.either import Right

        assert Ok is Right

    def test_err_is_left(self):
        from funstruct.monad.either import Left

        assert Err is Left

    def test_result_is_either(self):
        from funstruct.monad.either import Either

        assert Result is Either
