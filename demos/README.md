# Demos

Self-contained, runnable examples demonstrating funstruct patterns.

Each demo is a single Python file with a `main()` function. Run any demo with:

```bash
uv run python demos/01_result_pipeline.py
```

| Demo | What it shows |
|---|---|
| [`01_result_pipeline.py`](01_result_pipeline.py) | AsyncResult pipeline with @TryAsync, bind chains, >> operator |
| [`02_do_notation.py`](02_do_notation.py) | Do-notation variants: @do decorator, manual do, sync/async, mixing |
| [`03_tagless_final_intro.py`](03_tagless_final_intro.py) | Tagless final basics: same program, different effects (Result vs AsyncResult) |
| [`04_tagless_final_db.py`](04_tagless_final_db.py) | Swapping database backends: Postgres, in-memory, failing — same business logic |
| [`05_json_encoder.py`](05_json_encoder.py) | Custom typeclasses: JsonEncoder with composition and dataclass derivation |
| [`06_generic_functions.py`](06_generic_functions.py) | Generic functions with `F: Monad` trait bounds, summon resolution |
| [`07_reader_vs_cake.py`](07_reader_vs_cake.py) | Reader monad vs Cake pattern for dependency injection |
| [`08_custom_types.py`](08_custom_types.py) | Extending funstruct: define your own typeclasses, types, and instances |
| [`09_lenses.py`](09_lenses.py) | Optics: composable getters/setters for deeply nested immutable data |
| [`10_writer_stacktrace.py`](10_writer_stacktrace.py) | Writer monad: accumulate a call trace alongside computation |
| [`11_state_counter.py`](11_state_counter.py) | State monad: counter, stack machine, symbol table — pure stateful computation |

### Monad Transformers

These show the progression from the problem to the solution:

| Demo | What it shows |
|---|---|
| [`transformers/01_the_problem.py`](transformers/01_the_problem.py) | Nested monads (`Future[Option[User]]`) are painful to compose |
| [`transformers/02_option_t.py`](transformers/02_option_t.py) | OptionT flattens the pipeline — `lift_f`, `from_option`, `.run()` |
| [`transformers/03_alternative.py`](transformers/03_alternative.py) | Skip transformers — use one monad type everywhere (AsyncResult) |
