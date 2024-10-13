# funstruct

Some of my fav lil data structures. Heavily inspired by Scala.

These are not meant to be highly performant.

They are useful for smaller datasets and for personal scripts.

Like all functional stuctures, they play very well with recursive algos.

### Commands
This repo utilizes [just](https://github.com/casey/just), which defines a set of common commands.
Simply type `just` to see a list of available commands.
These commands are for testing, debugging, managing things, etc.

### Formatting/Linting
This repo utilizes [ruff](https://github.com/astral-sh/ruff). 
Setup: 
- [pre-commit](https://pre-commit.com/) with `poetry run pre-commit install`.
Formatting and linting will occur on commit.
If you want to run ruff outside of a commit: `just format` or `just lint`
