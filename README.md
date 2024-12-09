# Indiepixel

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

This uses `uv` but I think you can install the deps using `pip`
too. It's a Flask app: I run it like this:

```
python -m flask --debug run
```

After installing dependencies.

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
  - [ ] Image
  - [ ] PieChart
  - [ ] Plot
  - [ ] 'expand' option
  - [ ] WrappedText
- [x] Fonts
