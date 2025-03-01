# Indiepixel

[![PyPI - Version](https://img.shields.io/pypi/v/indiepixel)](https://pypi.org/project/indiepixel/)

_Contributions more than welcome!_

Basically… [pixlet](https://github.com/tidbyt/pixlet) in Python.

## Why?

This is an example for generating images for the Tidbyt
device, a nice LED display. The company that made the Tidbyt
got acquihired and won't be developing the software much
in the future.

Pixlet was very convenient, but is an oddball for a tech
stack: implemented in Go for people to consume in Starlark.
Starlark is a niche language. It'd be nice to support
a mainstream language.

This is a WIP implementation of the same concepts as pixlet
in Python.

## Development

### Environment setup

First make sure you have [uv installed](https://docs.astral.sh/uv/getting-started/installation/).

Install dependencies with:

```
uv sync
```

Install pre-commit hooks:

```
uv run pre-commit install
```

### Running examples

To run `examples/kitchen_sink.py`:

```
uv run indiepixel examples/cli/gradient.py
```

### Running tests

```
uv run pytest
```

### Linting and formatting

```
uv run pre-commit run --all-files
```

Or run ruff directly

```
uv run ruff check
uv run ruff format --check
```

## Publishing

This needs you to build before publishing:

1. Bump version in pyproject.toml
2. `uv build`
2. `uv publish`

## Status

_* = currently not tidbyt-compatible_

- [x] WebP generation
- [x] Rendering the tb-8 pixel font without anti-aliasing
- [x] Fonts
- Components
  - [x] Text
  - [x] Box*
  - [x] Rect*
  - [x] Column*
  - [x] Row
  - [x] Stack
  - [x] Circle
  - [x] PieChart
  - [x] Image
  - [x] Animation
  - [x] WrappedText
    - [ ] Resizing
    - [ ] Animation
  - [ ] Plot
  - [ ] 'expand' option
