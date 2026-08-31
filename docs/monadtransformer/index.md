# Monad Transformers

::: funstruct.monadtransformer

Transformers combine two monads into one, so you can write a flat pipeline
instead of nested pattern matching. Use `lift_f` to bring an inner monad
value into the transformer.

- [ReaderT](reader_t.md) — shared environment + inner monad
- [StateT](state_t.md) — threaded state + inner monad
- [EitherT](either_t.md) — error handling + inner monad
- [OptionT](option_t.md) — optionality + inner monad
- [WriterT](writer_t.md) — accumulated output + inner monad
