"""Tests for widgets."""

from __future__ import annotations

# ruff: noqa: D103
from indiepixel import Box, Rect, Root, Text


def test_rect() -> None:
    r = Rect(width=10, height=10, color="#f00")
    assert r.size((0, 0, 100, 100)) == (10, 10)


def test_text() -> None:
    t = Text(content="Hello world")
    assert t.size((0, 0, 100, 100)) == (51, 8)


def test_box() -> None:
    t = Text(content="Hello world")
    b = Box(t)
    # TODO: this is probably wrong, this should
    # be the same as the text that is contained!
    assert b.size((0, 0, 100, 100)) == (52, 9)


def test_root() -> None:
    r = Root(child=Rect(width=10, height=10, color="#000"))
    assert r.size((0, 0, 64, 32)) == (64, 32)
