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

## Getting started

First, install indiepixel with uv.

I use [mise](https://mise.jdx.dev/) to manage my versions, so I'd start out with

```sh
mise install python uv
```

But that's optional if you have global installations of Python and uv that you like.
Also: this process works without uv, with pip etc: if you're a Python expert, you can probably
piece that together.

Initialize your project:

```sh
uv init
```

Then install indiepixel

```
uv add indiepixel
```

Create a basic example: for example, copy [clock.py](https://github.com/tmcw/indiepixel/blob/main/examples/cli/clock.py) to the current directory.

Then run:

```
uv run indiepixel clock.py
```

Then, bam! You've got that clock rendering. If you want to get fancier,
you can create a directory of widgets and move `clock.py` into it, point
indiepixel at that, and it'll show all of them rendered in its web interface.

## Deploying

I like to deploy this with [Render](https://render.com/) but it's totally up to you. Again,
Python experts probably can just figure this out, but with Render:

Set up Render to deploy from a repo containing your `pyproject.toml` and `clock.py` (or
whatever widgets you've written)

Render doesn't support uv and it's rough to install. So dump those dependencies into
requirements.txt so the old-fashioned package managers can understand them:

```
uv pip freeze > requirements.txt
```

Your render start command will look like:

```
indiepixel src/clock.py
```

And add an environment variable like:

```
PYTHON_VERSION=3.13.2
```

To your environment so that it uses a modern version of Python.

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
