# Trait Patterns in Python

Three common trait/mixin patterns from Scala/Haskell, and how to
achieve them in Python with funstruct.

## 1. Selfless traits — use via mixin or import

In Scala, a "selfless trait" can be mixed in OR imported from a
companion object:

```scala
// Mix in
class Demo extends StandardLogger {
  info("hello")
}

// Import
import StandardLogger._
info("hello")
```

**In funstruct:** dot syntax (mixin) or summon (import):

```python
# Mixin style — dot syntax on the value
Some(10).map(lambda x: x + 1)

# Import style — summon the instance explicitly
F = summon(Monad, Option)
F.map(Some(10), lambda x: x + 1)
```

Both call the same underlying instance. Dot syntax is sugar over summon.

## 2. Stackable traits — compose behavior via decoration

In Scala, `abstract override` lets traits wrap parent behavior:

```scala
trait Logger {
  def message(msg: String): String
  def info(msg: String) = println("INFO: " + message(msg))
}

trait StandardLogger extends Logger {
  def message(msg: String) = msg
}

trait DateLogger extends Logger {
  abstract override def message(msg: String) =
    s"${LocalDateTime.now()}: ${super.message(msg)}"
}

// Stack them — DateLogger wraps StandardLogger
class Demo extends StandardLogger with DateLogger
```

**In Python:** use the Writer monad or explicit decoration:

```python
# Writer monad — each step adds to the accumulated output
from funstruct.monad.writer import ListWriter
from funstruct.typeclasses import Monoid

list_monoid = Monoid(typ=list, combine=lambda a, b: a + b, empty=[])

class Traced(ListWriter):
    _monoid = list_monoid

# Each step "stacks" its output on top of the previous
result = (
    Traced(10, ["[init] 10"])
    .bind(lambda x: Traced(x * 2, [f"[double] {x} → {x*2}"]))
    .bind(lambda x: Traced(x + 1, [f"[inc] {x} → {x+1}"]))
)
# value = 21, output = ["[init] 10", "[double] 10 → 20", "[inc] 20 → 21"]
```

Or with Python's standard decoration pattern:

```python
# Decorator pattern — wrap functions to add behavior
def with_logging(fn):
    def wrapper(*args, **kwargs):
        print(f"[{fn.__name__}] called with {args}")
        result = fn(*args, **kwargs)
        print(f"[{fn.__name__}] returned {result}")
        return result
    return wrapper

def with_timing(fn):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = fn(*args, **kwargs)
        print(f"[{fn.__name__}] took {time.time() - start:.3f}s")
        return result
    return wrapper

# Stack decorators — each wraps the previous
@with_logging
@with_timing
def process(x):
    return x * 2
```

## 3. Interface injection — ad-hoc mixin at instantiation

In Scala, you can mix in a trait when creating an instance:

```scala
class Door {
  def close() = println("SLAM!")
}

val door = new Door with Closeable  // ad-hoc mixin
closeAll(Seq(door, printWriter))    // Door is now Closeable
```

**In Python:** runtime class creation:

```python
from abc import ABC, abstractmethod

class Closeable(ABC):
    @abstractmethod
    def close(self): ...

class Door:
    def close(self):
        print("SLAM!")

# Ad-hoc mixin at runtime
ClosableDoor = type('ClosableDoor', (Door, Closeable), {})
door = ClosableDoor()

isinstance(door, Closeable)  # True
door.close()                 # SLAM!
```

Or more practically — just register a typeclass instance:

```python
from funstruct.typeclasses.utils.registry import register

class _DoorCloseable(Closeable):
    def close(self, door):
        print("SLAM!")

register(Closeable, Door, _DoorCloseable())

# Now any generic function that needs Closeable works with Door
def close_all(items, types):
    for item, typ in zip(items, types):
        summon(Closeable, typ).close(item)
```

## Comparison

| Pattern | Scala | Python / funstruct |
|---|---|---|
| Selfless | `extends Trait` or `import Companion._` | Dot syntax or summon |
| Stackable | `abstract override` | Writer monad or decorators |
| Interface injection | `new X with Y` | `type()` or `register()` |

## Which to use

- **Selfless** — use everywhere. Dot syntax for convenience, summon for generic code.
- **Stackable** — use Writer when you need accumulated output. Use decorators for cross-cutting concerns (logging, timing, caching).
- **Interface injection** — use `register()` to give existing types new capabilities without modifying them. This is the typeclass approach.
