# The Typeclass Pattern — JSON Serialization

The canonical example of how typeclasses work, translated from Scala.

## What are typeclasses?

Typeclasses are **ad-hoc polymorphism**: adding behavior to types you
don't own, without modifying them. The behavior isn't ON the type —
instead, we provide a mechanism for the runtime to LOOK UP the behavior
based on the type.

```text
str   → StringJSONWrite     (registered via for_type=str)
int   → IntJSONWrite        (registered via for_type=int)
list  → ListJSONWrite       (composes — summons the element's instance)
User  → DataclassJSONWrite  (derives — walks dataclass fields)
```

## The four parts

Every typeclass usage has exactly four parts:

1. **The typeclass** — the interface (what capability exists)
2. **The instances** — implementations (how each type does it)
3. **The generic function** — code that uses the capability
4. **The data types** — plain data, no typeclass knowledge

## Step 1: The typeclass

```python
from funstruct.typeclasses import BaseTypeclass

class JSONWrite(BaseTypeclass):
    """Typeclass: convert a value to a JSON string.

    Scala: trait JSONWrite[T] { def toJsonString(item: T): String }
    """
    @abstractmethod
    def to_json_string(self, item) -> str: ...
```

This says: "there exists a concept called JSONWrite, and it requires
a `to_json_string` operation." It says nothing about HOW any type
is serialized.

## Step 2: The generic function (context bound)

```python
def jsonify(item) -> str:
    """Scala: def jsonify[T: JSONWrite](item: T): String"""
    return summon(JSONWrite, type(item)).to_json_string(item)
```

`summon(JSONWrite, type(item))` is the **context bound** — it says
"I need a JSONWrite instance for whatever type `item` is." If one
doesn't exist, you get a clear `TypeError`.

In Scala, `[T: JSONWrite]` is syntactic sugar for the same thing:
the compiler passes the instance implicitly. In Python, `summon`
resolves it at runtime from the registry.

## Step 3: Instances for primitives

```python
class _StringJSONWrite(JSONWrite, for_type=str):
    """Scala: given JSONWrite[String] with ..."""
    def to_json_string(self, item: str) -> str:
        return json.dumps(item)

class _IntJSONWrite(JSONWrite, for_type=int):
    def to_json_string(self, item: int) -> str:
        return str(item)
```

`for_type=str` auto-registers: `summon(JSONWrite, str)` now returns
`_StringJSONWrite()`. No manual `register()` call needed.

## Step 4: Composable instances

```python
class _ListJSONWrite(JSONWrite, for_type=list):
    def to_json_string(self, items: list) -> str:
        if not items:
            return "[]"
        elem_writer = summon(JSONWrite, type(items[0]))
        elements = ", ".join(elem_writer.to_json_string(item) for item in items)
        return f"[{elements}]"
```

The list instance **summons the element's instance**. `jsonify([1,2,3])`
uses `IntJSONWrite` for each element. `jsonify(["a","b"])` uses
`StringJSONWrite`. No special-casing — composition via summon.

## Step 5: Derived instances (dataclasses)

```python
class DataclassJSONWrite(JSONWrite):
    def to_json_string(self, item) -> str:
        cls_name = type(item).__name__
        field_strings = []
        for f in fields(item):
            value = getattr(item, f.name)
            writer = summon(JSONWrite, type(value))
            field_strings.append(f'"{f.name}": {writer.to_json_string(value)}')
        return f'{{"{cls_name}": {{{", ".join(field_strings)}}}}}'

# One line per type
register(JSONWrite, Person, DataclassJSONWrite())
register(JSONWrite, Employee, DataclassJSONWrite())
```

`DataclassJSONWrite` walks the fields and summons per-field. Nested
dataclasses work automatically — `Employee` has a `Person` field,
and `Person` has `str` and `int` fields. Each resolves via the registry.

## Step 6: Plain data types

```python
@dataclass(frozen=True)
class Person:
    name: str
    age: int

@dataclass(frozen=True)
class Employee:
    person: Person
    address: Address
    salary: float
```

No `to_json` method, no `JSONWrite` inheritance. Plain data.

## The result

```python
jsonify("hello")        # '"hello"'
jsonify(42)             # '42'
jsonify([1, 2, 3])      # '[1, 2, 3]'
jsonify(Person("Alice", 30))
# '{"Person": {"name": "Alice", "age": 30}}'
jsonify(Employee(person, address, 120000.0))
# '{"Employee": {"person": {"Person": ...}, "address": {"Address": ...}, "salary": 120000.0}}'
```

One generic function, works for every type that has an instance.
New types get support by registering an instance — no modification
to `jsonify`, and no modification to the type itself.

## See also

- `demos/15_typeclass_pattern_json.py` — full runnable example
- `funstruct/playground/mt14.py` — same, as a local playground script
- `guides/typeclass_pattern_ordering.md` — the Ordering example
- `guides/generic_programming.md` — programming with context bounds
