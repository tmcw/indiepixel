# Indiepixel

![PyPI - Version](https://img.shields.io/pypi/v/indiepixel)

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
uv run examples/kitchen_sink.py
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

## Status

- [x] WebP generation
- [x] Rendering the tb-8 pixel font without anti-aliasing
- Components
  - [x] Text
  - [x] Box
  - [x] Rect
  - [x] Column
  - [x] Row
  - [ ] Animation
  - [x] Image
    - [ ] Resizing
    - [ ] Animation
  - [ ] PieChart
  - [ ] Plot
  - [ ] 'expand' option
  - [ ] WrappedText
- [x] Fonts
