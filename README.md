# tidbyt-py

There's no snappy name yet, but basically… [pixlet](https://github.com/tidbyt/pixlet)
in Python?

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

## Status

- [x] WebP generation
- [x] Rendering the tb-8 pixel font without anti-aliasing
- Components
  - [ ] Text _in progress_
  - [ ] Box _in progress_
  - [ ] Animation
  - [ ] Column
  - [ ] Image
  - [ ] PieChart
  - [ ] Plot
  - [ ] Row
  - [ ] WrappedText

