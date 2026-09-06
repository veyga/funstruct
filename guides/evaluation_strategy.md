# Evaluation Strategy

## Strict by default

Python is a strictly (eagerly) evaluated language. funstruct inherits
this — expressions are evaluated when encountered, arguments are
evaluated before being passed to functions.

This means:

```python
# Both branches of this are evaluated immediately:
Ok(expensive_computation()).map(transform)  # expensive_computation() runs NOW
Err("skip").map(transform)                 # map is skipped, but Err("skip") already exists
```

In Haskell, `expensive_computation` wouldn't run until its value is
actually needed. In Python, it runs at the call site regardless.

## Deferred execution (not true laziness)

Some funstruct types wrap a function or coroutine — the computation
doesn't execute until you explicitly trigger it:

```python
# AsyncResult — lazy until await
pipeline = AsyncResult.pure(10).map(expensive)  # nothing runs yet
result = await pipeline                         # NOW it runs

# Reader — lazy until .run(ctx)
pipeline = Reader(lambda ctx: ctx["db"].query())  # nothing runs yet
result = pipeline.run(app_context)                # NOW it runs

# State — lazy until .run(initial)
pipeline = State(lambda s: (s + 1, s))  # nothing runs yet
state, value = pipeline.run(0)          # NOW it runs

# Future — lazy until await
pipeline = Future.pure(42).map(expensive)  # nothing runs yet
result = await pipeline                    # NOW it runs
```

This is **deferred execution**, not Haskell-style laziness. The
difference: Haskell's laziness is automatic and pervasive (every value
is lazy by default). funstruct's deferral is explicit and limited to
types that wrap functions or coroutines.

## Strict data structures

All funstruct collections are fully strict:

```python
CList.new(1, 2, 3)      # all 3 cons cells exist immediately
frozendict({"a": 1})     # entire HAMT built immediately
Tree(Leaf(1), Leaf(2))   # entire tree exists immediately
```

There are no infinite data structures. You cannot write:

```python
# This is NOT possible in funstruct (yet):
nats = 0 :: 1 :: 2 :: ...  # infinite list — requires laziness
```

The **Stream** type on the roadmap would add lazy, potentially
infinite sequences.

## Do-notation and generators

Python's generators provide a limited form of laziness — each `yield`
pauses execution until the next value is requested:

```python
@Result.do
def pipeline():
    x = yield Ok(10)       # pauses here, resumes when x is needed
    y = yield Ok(x + 1)    # pauses here
    return x + y            # final value
```

This is why do-notation works for short-circuiting — if `yield` gets
an `Err`, the generator stops and the error propagates. No subsequent
`yield` is reached.

## Summary

| Evaluation | What | Examples |
|------------|------|---------|
| **Strict** | Data structures, Option, Either, Result, Validated | CList, frozendict, Some, Ok, Err |
| **Deferred** | Async computations, environment/state readers | AsyncResult, Future, Reader, State |
| **Semi-lazy** | Generator-based do-notation | `@Result.do`, `@Option.do` |
| **Lazy** | Not yet available | Roadmap: Stream |
