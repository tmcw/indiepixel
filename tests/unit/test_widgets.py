"""Tests for widgets."""

from __future__ import annotations

# ruff: noqa: D103
from indiepixel import Box, Circle, PieChart, Rect, Root, Row, Text, WrappedText, render


def test_rect() -> None:
    r = Rect(width=10, height=10, color="#f00")
    assert r.size((0, 0, 100, 100)) == (10, 10)


def test_text() -> None:
    t = Text(content="Hello world")
    assert t.size((0, 0, 100, 100)) == (51, 8)


def test_wrapped_text_single_line() -> None:
    wt = WrappedText(content="Hi")
    assert wt.wrap_text((0, 0, 64, 32)) == "Hi"


def test_wrapped_text_size() -> None:
    wt = WrappedText(content="No trains scheduled")
    # Widest line ("scheduled") is 42px; 2 lines of 8px
    assert wt.size((0, 0, 64, 32)) == (42, 16)


def test_wrapped_text_size_with_width_and_height() -> None:
    wt = WrappedText(content="No trains scheduled", width=50, height=8)
    assert wt.size((0, 0, 64, 32)) == (50, 8)


def test_wrapped_text_empty() -> None:
    # No width; one blank 8px line
    assert WrappedText(content="").size((0, 0, 64, 32)) == (0, 8)


def test_box() -> None:
    t = Text(content="Hello world")
    b = Box(t)
    assert b.size((0, 0, 100, 100)) == (51, 8)


def test_box_padding() -> None:
    b = Box(Text(content="Hello world"), padding=2)
    assert b.size((0, 0, 100, 100)) == (55, 12)


def painted_size(widget) -> tuple[int, int]:
    bbox = render(Root(child=widget, size=(32, 32)))[0].getbbox()
    assert bbox is not None
    x0, y0, x1, y1 = bbox
    return (x1 - x0, y1 - y0)


def test_rect_paints_its_size() -> None:
    assert painted_size(Rect(width=8, height=8, color="#fff")) == (8, 8)


def test_circle_paints_its_size() -> None:
    assert painted_size(Circle(diameter=10, color="#fff")) == (10, 10)


def test_piechart_paints_its_size() -> None:
    pie = PieChart(diameter=10, colors=["#fff", "#f00"], weights=[1, 1])
    assert painted_size(pie) == (10, 10)


def test_box_paints_its_size() -> None:
    b = Box(Rect(width=8, height=8, color="#000"), padding=2, background="#fff")
    assert painted_size(b) == (12, 12)


def test_wrapped_text_aligns_within_its_width() -> None:
    unsized = WrappedText(content="Hi", align="right")
    sized = WrappedText(content="Hi", width=20, align="right")
    im = render(Root(child=Row(children=[unsized, sized]), size=(64, 32)))[0]
    # Unsized "Hi" (9px) isn't shifted, so text starts at x=0.
    # Sized "Hi" is right-aligned in x=9..29, so text ends at x=28.
    assert im.getbbox() == (0, 1, 28, 7)


def test_root() -> None:
    r = Root(child=Rect(width=10, height=10, color="#000"))
    assert r.size((0, 0, 64, 32)) == (64, 32)
