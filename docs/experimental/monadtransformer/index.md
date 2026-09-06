# Monad Transformers

> **Experimental** — the transformer API is alpha and may change. For most
> use cases, plain monads with `do`-notation and `fold` are sufficient.
> Reach for transformers only when you need to combine multiple effects
> in a single pipeline.

::: funstruct.experimental.monadtransformer

Transformers combine two monads into one, so you can write a flat pipeline
instead of nested pattern matching. Use `lift_f` to bring an inner monad
value into the transformer, and `.run()` to unwrap at the boundary.

```python
# Without transformer — nested pattern matching at every step:
result = fetch_user(id)  # Either[Err, Option[User]]
match result:
    case Left(e): ...       # handle error
    case Right(Nothing()): ...  # handle absence
    case Right(Some(user)): ... # finally, the value

# With OptionT — one flat pipeline:
pipeline = (
    OptionT(fetch_user(id))
    .bind(lambda user: OptionT(get_email(user)))
    .map(lambda email: email.upper())
)
pipeline.run()  # Either[Err, Option[str]]
```

- [ReaderT](reader_t.md) — shared environment + inner monad
- [StateT](state_t.md) — threaded state + inner monad
- [EitherT](either_t.md) — error handling + inner monad
- [OptionT](option_t.md) — optionality + inner monad
- [WriterT](writer_t.md) — accumulated output + inner monad
