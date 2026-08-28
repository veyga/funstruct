from funstruct.monad.either import Either, Right, Left, attempt
from funstruct.collections.cons import Cons, Nil, CList
from tests.laws import assert_functor_laws, assert_monad_laws


class TestRight:
    def test_map(self):
        assert Right(1).map(lambda x: x + 10) == Right(11)

    def test_bind(self):
        assert Right(1).bind(lambda x: Right(x + 10)) == Right(11)

    def test_bind_to_left(self):
        assert Right(1).bind(lambda x: Left("fail")) == Left("fail")

    def test_ap(self):
        assert Right(1).ap(Right(2)) == Right((1, 2))

    def test_ap_left(self):
        assert Right(1).ap(Left("err")) == Left("err")

    def test_or_else(self):
        assert Right(1).or_else(lambda e: Right(99)) == Right(1)

    def test_get_or_else(self):
        assert Right(1).get_or_else(99) == 1

    def test_fold(self):
        assert Right(1).fold(lambda e: "bad", lambda a: f"got {a}") == "got 1"

    def test_swap(self):
        assert Right(1).swap() == Left(1)

    def test_is_right(self):
        assert Right(1).is_right is True
        assert Right(1).is_left is False

    def test_rshift(self):
        assert (Right(1) >> (lambda x: Right(x + 10))) == Right(11)

    def test_map2(self):
        assert Right(2).map2(Right(3), lambda a, b: a + b) == Right(5)

    def test_map2_left(self):
        assert Right(2).map2(Left("err"), lambda a, b: a + b) == Left("err")


class TestLeft:
    def test_map(self):
        assert Left("err").map(lambda x: x + 10) == Left("err")

    def test_bind(self):
        assert Left("err").bind(lambda x: Right(x + 10)) == Left("err")

    def test_ap(self):
        assert Left("err").ap(Right(1)) == Left("err")

    def test_or_else(self):
        assert Left("err").or_else(lambda e: Right("recovered")) == Right("recovered")

    def test_or_else_to_left(self):
        assert Left("err").or_else(lambda e: Left("still bad")) == Left("still bad")

    def test_get_or_else(self):
        assert Left("err").get_or_else(99) == 99

    def test_fold(self):
        assert Left("err").fold(lambda e: f"error: {e}", lambda a: "ok") == "error: err"

    def test_swap(self):
        assert Left("err").swap() == Right("err")

    def test_is_left(self):
        assert Left("err").is_left is True
        assert Left("err").is_right is False


class TestDo:
    def test_success(self):
        def pipeline():
            x = yield Right(1)
            y = yield Right(x + 10)
            return x + y

        assert Either.do(pipeline) == Right(12)

    def test_short_circuits(self):
        def pipeline():
            x = yield Right(1)
            y = yield Left("boom")
            return x + y

        assert Either.do(pipeline) == Left("boom")

    def test_multiple_binds(self):
        def pipeline():
            a = yield Right(1)
            b = yield Right(2)
            c = yield Right(3)
            return a + b + c

        assert Either.do(pipeline) == Right(6)


class TestAttempt:
    def test_success(self):
        @attempt
        def divide(a, b):
            return a / b

        assert divide(10, 2) == Right(5.0)

    def test_failure(self):
        @attempt
        def divide(a, b):
            return a / b

        result = divide(10, 0)
        assert result.is_left
        match result:
            case Left(e):
                assert type(e) is ZeroDivisionError

    def test_class_method(self):
        result = Either.attempt(lambda: int("abc"))
        assert result.is_left
        match result:
            case Left(e):
                assert type(e) is ValueError


class TestSequenceTraverse:
    def test_sequence_all_right(self):
        items = Cons(Right(1), Cons(Right(2), Cons(Right(3), Nil())))
        assert Either.sequence(items) == Right(CList.from_iterable([1, 2, 3]))

    def test_sequence_with_left(self):
        items = Cons(Right(1), Cons(Left("err"), Cons(Right(3), Nil())))
        assert Either.sequence(items) == Left("err")

    def test_sequence_first_left_wins(self):
        items = Cons(Left("first"), Cons(Left("second"), Nil()))
        assert Either.sequence(items) == Left("first")

    def test_traverse_all_succeed(self):
        values = CList.from_iterable([1, 2, 3])
        result = Either.traverse(values, lambda x: Right(x * 10))
        assert result == Right(CList.from_iterable([10, 20, 30]))

    def test_traverse_short_circuits(self):
        values = CList.from_iterable([1, 0, 3])
        result = Either.traverse(
            values,
            lambda x: Right(x) if x != 0 else Left("zero"),
        )
        assert result == Left("zero")


class TestEquality:
    def test_right_eq(self):
        assert Right(1) == Right(1)
        assert Right(1) != Right(2)

    def test_left_eq(self):
        assert Left("a") == Left("a")
        assert Left("a") != Left("b")

    def test_cross(self):
        assert Right(1) != Left(1)
        assert Left(1) != Right(1)


class TestLaws:
    def test_functor_laws(self):
        assert_functor_laws(Right(42))

    def test_monad_laws(self):
        assert_monad_laws(
            pure_fn=Right,
            m=Right(10),
            f=lambda x: Right(x + 1),
            g=lambda x: Right(x * 2),
        )

    def test_monad_laws_left_propagation(self):
        assert_monad_laws(
            pure_fn=Right,
            m=Left("err"),
            f=lambda x: Right(x + 1),
            g=lambda x: Right(x * 2),
        )
