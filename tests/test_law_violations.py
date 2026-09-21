"""Tests that verify our laws CATCH violations.

These are negative tests — they prove the law assertions actually fail
when given something that doesn't satisfy the laws.

Also demonstrates which structures accept Semigroup vs require Monoid,
and provides examples of BROKEN implementations that violate laws.

Summary of violations:

    Broken Implementation           | Law Violated          | What's Wrong
    --------------------------------+-----------------------+---------------------------------
    IntSubtract (Semigroup)         | Associativity         | (a-b)-c != a-(b-c)
    FloatDivide (Semigroup)         | Associativity         | (a/b)/c != a/(b/c)
    BadIntMonoid (empty=1)          | Identity              | combine(1, a) != a
    CountingBox (increments on map) | Functor identity      | map(id) != id
    DoublingBox (applies f twice)   | Functor composition   | map(f).map(g) != map(g∘f)
    TaggedBox (pure adds a tag)     | Monad left identity   | pure(a).bind(f) != f(a)
    SemigroupWriter (no empty)      | Writer needs Monoid   | pure crashes — no identity

Semigroup vs Monoid requirement:

    Structure  | Requires  | Why
    -----------+-----------+-------------------------------------------
    Validated  | Semigroup | ap accumulates errors via combine, no empty needed
    Writer     | Monoid    | pure needs empty for the initial output
"""

import pytest

from funstruct.typeclasses import Monoid, Semigroup
from funstruct.typeclasses.functor import Functor
from funstruct.typeclasses.monad import Monad
from funstruct.types.cons import Cons, Nil
from funstruct.types.validated import Invalid, Valid
from funstruct.types.writer import Writer
from tests.laws import (
    assert_functor_laws,
    assert_monad_laws,
    assert_monoid_laws,
    assert_semigroup_laws,
)


class _IntSubtract(Semigroup):
    def combine(self, a, b):
        return a - b


class _FloatDivide(Semigroup):
    def combine(self, a, b):
        return a / b


class _IntAdd(Semigroup):
    def combine(self, a, b):
        return a + b


class _IntAddMonoid(Monoid):
    def combine(self, a, b):
        return a + b

    def empty(self):
        return 0


class _BadIntMonoid(Monoid):
    def combine(self, a, b):
        return a + b

    def empty(self):
        return 1  # WRONG: 1 is not identity for addition


class TestAssociativityViolation:
    """Ints under subtraction are NOT associative: (a - b) - c != a - (b - c)."""

    def test_subtraction_violates_associativity(self):
        with pytest.raises(AssertionError, match="associativity"):
            assert_semigroup_laws(10, 3, 1, sg=_IntSubtract())

    def test_division_violates_associativity(self):
        with pytest.raises(AssertionError, match="associativity"):
            assert_semigroup_laws(12.0, 3.0, 2.0, sg=_FloatDivide())


class TestWriterRequiresMonoid:
    """Writer needs Monoid (not just Semigroup) because `pure` needs `empty`.

    Writer.pure(value) constructs a writer with the identity output —
    the "zero" for the accumulator. Without `empty`, there's no way to
    lift a plain value into a Writer without specifying initial output.
    This is why Writer is parametrized over a Monoid, not a Semigroup.
    """

    def test_writer_with_semigroup_fails_on_pure(self):
        class BadWriter(Writer):
            _monoid = _IntAdd()

        with pytest.raises(AttributeError):
            BadWriter.pure(42)

    def test_writer_with_monoid_succeeds(self):
        GoodWriter = Writer.for_monoid(_IntAddMonoid(), "GoodWriter")

        w = GoodWriter.pure(42)
        assert w.value == 42
        assert w.output == 0

    def test_writer_pure_uses_empty_as_identity(self):
        """pure(a).bind(f) == f(a) only holds when output starts at empty."""
        CountWriter = Writer.for_monoid(_IntAddMonoid(), "CountWriter")

        f = lambda x: CountWriter(x + 1, 1)

        # Left identity: pure(a).bind(f) == f(a)
        assert CountWriter.pure(5).bind(f) == f(5)


class TestSemigroupSufficesForValidated:
    """Validated only needs Semigroup — no `empty` required.

    Errors accumulate via combine, but there's never a "start from nothing"
    case — errors only exist when validation already failed.
    """

    def test_validated_accumulates_via_semigroup_combine(self):
        """Invalid.product accumulates errors via + (CList's semigroup combine)."""
        a = Invalid(Cons(1, Nil()))
        b = Invalid(Cons(2, Nil()))
        result = a.product(b)
        assert result == Invalid(Cons(1, Cons(2, Nil())))

    def test_validated_with_monoid(self):
        """Monoid also works (it's a Semigroup with extra)."""
        a = Invalid(Cons("err1", Nil()))
        b = Invalid(Cons("err2", Nil()))
        result = a.product(b)
        assert result == Invalid(Cons("err1", Cons("err2", Nil())))

    def test_valid_needs_no_semigroup(self):
        """Valid.product tuples values."""
        assert Valid(1).product(Valid(2)) == Valid((1, 2))

    def test_valid_ap_applies_function(self):
        """Valid.ap applies a wrapped function."""
        assert Valid(lambda x: x + 1).ap(Valid(2)) == Valid(3)


class TestSemigroupVsMonoidOnWriter:
    """Writer.bind only uses combine (Semigroup), but Writer.pure needs empty
    (Monoid).

    This means: if you NEVER call pure/tell-with-empty, a semigroup
    technically works for bind. But pure will crash. This is why
    Writer demands a Monoid at the type level.
    """

    def test_bind_uses_combine(self):
        """bind combines output from both steps."""
        TestIntWriter = Writer.for_monoid(_IntAddMonoid(), "IntWriter_test")

        w1 = TestIntWriter(1, 10)
        w2 = w1.bind(lambda x: TestIntWriter(x + 1, 20))
        assert w2.value == 2
        assert w2.output == 30

    def test_pure_crashes_without_empty(self):
        """pure needs empty — semigroup lacks it."""

        class SemigroupWriter(Writer):
            _monoid = _IntAdd()

        with pytest.raises(AttributeError):
            SemigroupWriter.pure(42)

    def test_monoid_satisfies_both(self):
        """Monoid has combine AND empty — everything works."""
        TestMonoidWriter = Writer.for_monoid(_IntAddMonoid(), "MonoidWriter_test")

        w = TestMonoidWriter.pure(42)
        assert w.value == 42
        assert w.output == 0
        w2 = w.bind(lambda x: TestMonoidWriter(x + 1, 5))
        assert w2.value == 43
        assert w2.output == 5


# ──────────────────────────────────────────────────────────────────────
# BAD IMPLEMENTATIONS — what NOT to do
# ──────────────────────────────────────────────────────────────────────


class TestBrokenMonoid:
    """A monoid where `empty` is NOT a true identity."""

    def test_bad_empty_violates_identity(self):
        """combine(empty, a) != a when empty isn't neutral."""
        with pytest.raises(AssertionError, match="identity"):
            assert_monoid_laws(5, sg=_BadIntMonoid())


class TestBrokenFunctor:
    """A functor where map(identity) != identity — map has side effects."""

    def test_map_identity_violated(self):
        """map(lambda x: x) should return the same structure unchanged."""

        class CountingBox(Functor):
            def __init__(self, value, count=0):
                self.value = value
                self.count = count

            def map(self, f):
                # BUG: increments count on every map, even identity
                return CountingBox(f(self.value), self.count + 1)

            def __eq__(self, other):
                return self.value == other.value and self.count == other.count

        with pytest.raises(AssertionError, match="identity"):
            assert_functor_laws(CountingBox(42))

    def test_map_composition_violated(self):
        """map(f).map(g) != map(g∘f) when map applies f twice."""

        class DoublingBox(Functor):
            """Applies f twice — passes identity (id∘id=id) but breaks composition.

            map(f).map(g) = g(g(f(f(x))))
            map(g∘f)      = g∘f(g∘f(x))
            These diverge for non-idempotent f and g.
            """

            def __init__(self, value):
                self.value = value

            def map(self, f):
                return DoublingBox(f(f(self.value)))

            def __eq__(self, other):
                return self.value == other.value

        # Our law uses f=lambda x: (x,"f"), g=lambda x: (x,"g")
        # map(f).map(g): f(f(5)) = ((5,"f"),"f"), g(g(that)) = deep nesting
        # map(g∘f): (g∘f)((g∘f)(5)) = different nesting
        with pytest.raises(AssertionError, match="composition"):
            assert_functor_laws(DoublingBox(5))


class TestBrokenMonad:
    """A monad that violates left identity: pure(a).bind(f) != f(a)."""

    def test_left_identity_violated(self):
        """pure adds extra state that f(a) doesn't have."""

        class TaggedBox(Monad):
            def __init__(self, value, tag=""):
                self.value = value
                self.tag = tag

            @classmethod
            def pure(cls, value):
                # BUG: pure adds a tag that raw construction doesn't
                return cls(value, tag="pure")

            def map(self, f):
                return TaggedBox(f(self.value), self.tag)

            def bind(self, f):
                result = f(self.value)
                return TaggedBox(result.value, self.tag + result.tag)

            @classmethod
            def do(cls, gen_fn):
                raise NotImplementedError

            def __eq__(self, other):
                return self.value == other.value and self.tag == other.tag

        f = lambda x: TaggedBox(x + 1, tag="f")

        # pure(5).bind(f) = TaggedBox(6, "puref")
        # f(5)            = TaggedBox(6, "f")
        # These differ! Left identity violated.
        with pytest.raises(AssertionError, match="left identity"):
            assert_monad_laws(
                pure_fn=TaggedBox.pure,
                m=TaggedBox(10),
                f=f,
                g=lambda x: TaggedBox(x * 2, tag="g"),
            )
