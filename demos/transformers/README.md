# Monad Transformer Demos

These demos show the progression from the problem (uncomposable monads)
to the solutions (transformers and alternatives).

| Demo | What it shows |
|------|---------------|
| `01_the_problem.py` | Nested monads (`Future[Option[User]]`) are painful to compose |
| `02_option_t.py` | OptionT flattens the pipeline — `lift_f`, `from_option`, `.run()` |
| `03_alternative.py` | Skip transformers — use one monad type everywhere (AsyncResult) |

Run any demo: `uv run python demos/transformers/01_the_problem.py`
