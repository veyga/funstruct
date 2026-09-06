# Functional Anti-Patterns

Common mistakes when adopting functional programming in Python.

## 1. Wrapping everything in a monad

```python
# BAD — Option adds nothing here
def add(a: int, b: int) -> Option[int]:
    return Some(a + b)

# GOOD — plain function, can't fail
def add(a: int, b: int) -> int:
    return a + b
```

Use monads at **boundaries** — where things can actually fail, be
absent, or produce side effects. Pure computations don't need wrapping.

**Rule of thumb:** if a function can't fail, return a plain value.

## 2. Catching and re-wrapping known exceptions

```python
# BAD — catching what you just threw
def get_user(id: int) -> Result[User]:
    try:
        user = db.query(id)
        if user is None:
            raise ValueError("not found")
        return Ok(user)
    except ValueError as e:
        return Err(e)

# GOOD — use Result directly, no exceptions
def get_user(id: int) -> Result[User]:
    user = db.query(id)
    if user is None:
        return Err(ValueError("not found"))
    return Ok(user)

# BEST — use @Try only at the boundary with exception-throwing code
@Try
def get_user(id: int) -> User:
    return db.query_or_raise(id)  # let @Try catch it
```

`@Try` is for wrapping code you don't control. If you control the
logic, return `Ok`/`Err` directly.

## 3. Nested monads without transformers or unification

```python
# BAD — Future[Option[Result[User]]]
def get_user(id) -> Future[Option[Result[User]]]:
    ...
# Now every caller unwraps 3 layers

# GOOD — pick ONE monad for your pipeline
def get_user(id) -> AsyncResult[User]:
    ...
# Clean composition: .bind(), .map(), @do
```

Don't stack monads. Either use a transformer (`OptionT`, `EitherT`)
or unify on a single type (usually `AsyncResult` or `Result`).

## 4. Overly abstract code

```python
# BAD — abstraction for abstraction's sake
def process(F: Monad, G: MonadError, H: Traversable, fa):
    return G.handle_error_with(
        H.traverse(fa, lambda x: F.map(F.pure(x), str), F),
        lambda e: F.pure("default")
    )

# GOOD — just write the concrete code
def process(items: CList[int]) -> Option[CList[str]]:
    return Option.traverse(items, lambda x: Some(str(x)))
```

Use typeclass abstraction (summon, F: Monad) when you actually need
to support multiple types. For one concrete type, just use it directly.

**Rule:** if your function only ever runs with `Option`, type it as
`Option`, not `F: Monad`.

## 5. do-notation for one or two steps

```python
# BAD — do-notation overhead for a single bind
@Result.do
def pipeline():
    x = yield Ok(10)
    return x + 1

# GOOD — just use map
Ok(10).map(lambda x: x + 1)
```

Do-notation pays off at 3+ steps. For 1-2 steps, `map` or `bind` is
clearer and faster (~2x, see benchmarks).

## 6. Pattern matching where map/bind suffice

```python
# BAD — manual pattern matching
match get_user(id):
    case Some(user):
        match get_email(user):
            case Some(email):
                return Some(email.upper())
            case Nothing():
                return Nothing()
    case Nothing():
        return Nothing()

# GOOD — let bind handle the short-circuiting
get_user(id).bind(get_email).map(str.upper)
```

Pattern matching is for *consuming* a final result. For *composing*
operations, use `map`/`bind` — that's what they're for.

## 7. Mutation hidden inside monadic code

```python
# BAD — mutating a shared list inside map
results = []
def collect(x):
    results.append(x)  # MUTATION — defeats the purpose
    return x

Some(10).map(collect)  # side effect hidden inside "functional" code

# GOOD — use Writer for accumulation
@TraceWriter.do
def pipeline():
    x = yield TraceWriter(10, ["started"])
    y = yield TraceWriter(x + 1, ["incremented"])
    return y
```

If you need to accumulate, use Writer. If you need state, use State.
Don't smuggle mutation inside `map`/`bind`.

## 8. Ignoring the error rail

```python
# BAD — extracting with get_or_else immediately
user = get_user(id).get_or_else(default_user)
email = get_email(user).get_or_else("unknown@unknown.com")
prefs = get_prefs(user).get_or_else(default_prefs)

# GOOD — stay on the rails, unwrap once at the boundary
@Result.do
def pipeline(id):
    user = yield get_user(id)
    email = yield get_email(user)
    prefs = yield get_prefs(user)
    return Profile(user, email, prefs)

match pipeline(id):
    case Ok(profile): render(profile)
    case Err(e): render_error(e)
```

`get_or_else` is for the boundary — where you finally need a plain
value. Inside a pipeline, stay monadic and let errors propagate.

## 9. Creating typeclasses for things that aren't typeclasses

```python
# BAD — this is just a regular interface
class UserService(BaseTypeclass):
    @abstractmethod
    def get_user(self, id): ...
    @abstractmethod
    def save_user(self, user): ...

# GOOD — this is a regular Protocol/ABC, not a typeclass
class UserService(Protocol):
    def get_user(self, id: int) -> Result[User]: ...
    def save_user(self, user: User) -> Result[None]: ...
```

Typeclasses are for **capabilities that multiple unrelated types share**
(Functor, Monad, Ordering). Business interfaces (UserService,
EmailSender) are just Protocols/ABCs.

**Typeclass test:** "Does `int`, `str`, AND `User` need this?" If yes,
it might be a typeclass. If only `UserService` needs it, it's a Protocol.

## 10. Premature typeclass abstraction

```python
# BAD — abstracting over the effect type when you have one effect
def get_user(F: MonadError, id: int):
    ...
def save_user(F: MonadError, user: User):
    ...
# Every function takes F — massive boilerplate for no benefit

# GOOD — use Result directly until you actually need polymorphism
def get_user(id: int) -> Result[User]:
    ...
def save_user(user: User) -> Result[None]:
    ...
```

Use `F: Monad` when you have multiple callers that need different
effects (tagless final, library code). For application code with one
effect type, just use it directly.

## Summary

| Anti-pattern | Fix |
|---|---|
| Wrapping pure functions in monads | Return plain values |
| Catching your own exceptions | Return Ok/Err directly |
| Nested monads | Unify on one type or use transformers |
| Over-abstraction | Use concrete types until you need polymorphism |
| do-notation for 1-2 steps | Use map/bind directly |
| Pattern matching for composition | Use map/bind |
| Hidden mutation | Use Writer/State |
| Immediate get_or_else | Stay monadic, unwrap at boundary |
| Business interfaces as typeclasses | Use Protocol/ABC |
| Premature typeclass abstraction | Use concrete types first |
