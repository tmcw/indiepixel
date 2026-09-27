"""
Tests for pixlet compatibility.

Verifies that widgets behave according to the pixlet specification
documented at https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md
"""

# ruff: noqa: D103
from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image as ImagePIL
from PIL import ImageDraw
from syrupy.extensions.image import PNGImageSnapshotExtension

from indiepixel import Column, Padding, Plot, Rect, Root, Row, Text


@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(PNGImageSnapshotExtension)


@pytest.fixture
def image() -> ImagePIL.Image:
    return ImagePIL.new("RGB", (64, 32))


@pytest.fixture
def image_draw(image: ImagePIL.Image) -> ImageDraw.ImageDraw:
    return ImageDraw.ImageDraw(image)


@pytest.fixture
def render_widget(image, image_draw):
    """Render a widget to PNG image data."""

    def render_widget_impl(widget) -> bytes:
        image_draw.rectangle([0, 0, 63, 31], fill=(0, 0, 0))
        widget.paint(image_draw, image, (0, 0, 64, 32), 0)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()
        buffer.close()
        return png_bytes

    return render_widget_impl


BOUNDS = (0, 0, 64, 32)


# --- Root ---


def test_root_default_size() -> None:
    """Root provides a 64x32 canvas."""
    root = Root(child=Rect(width=10, height=10, color="#fff"))
    assert root.size(BOUNDS) == (64, 32)


def test_root_custom_size() -> None:
    root = Root(child=Rect(width=10, height=10, color="#fff"), size=(128, 64))
    assert root.size(BOUNDS) == (128, 64)


def test_root_frame_count() -> None:
    root = Root(child=Rect(width=10, height=10, color="#fff"))
    assert root.frame_count() == 1


# --- Row ---


def test_row_shrinks_to_fit() -> None:
    """Row is as small as possible while holding all children."""
    row = Row(
        children=[
            Rect(width=10, height=5, color="#f00"),
            Rect(width=20, height=10, color="#0f0"),
        ]
    )
    assert row.size(BOUNDS) == (30, 10)


def test_row_expanded_fills_width() -> None:
    """Expanded Row fills available horizontal space."""
    row = Row(children=[Rect(width=10, height=5, color="#f00")], expanded=True)
    assert row.size(BOUNDS) == (64, 5)


def test_row_expand_compat() -> None:
    """The old 'expand' parameter still works."""
    row = Row(children=[Rect(width=10, height=5, color="#f00")], expand=True)
    assert row.size(BOUNDS) == (64, 5)


def test_row_main_align_end(snapshot, render_widget) -> None:
    row = Row(
        children=[
            Rect(width=5, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        expanded=True,
        main_align="end",
    )
    assert render_widget(row) == snapshot


def test_row_main_align_center(snapshot, render_widget) -> None:
    row = Row(
        children=[
            Rect(width=5, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        expanded=True,
        main_align="center",
    )
    assert render_widget(row) == snapshot


def test_row_main_align_space_between(snapshot, render_widget) -> None:
    row = Row(
        children=[
            Rect(width=5, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        expanded=True,
        main_align="space_between",
    )
    assert render_widget(row) == snapshot


def test_row_cross_align_center(snapshot, render_widget) -> None:
    row = Row(
        children=[
            Rect(width=5, height=10, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        cross_align="center",
    )
    assert render_widget(row) == snapshot


def test_row_cross_align_end(snapshot, render_widget) -> None:
    row = Row(
        children=[
            Rect(width=5, height=10, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        cross_align="end",
    )
    assert render_widget(row) == snapshot


# --- Column ---


def test_column_shrinks_to_fit() -> None:
    """Column is as small as possible while holding all children."""
    col = Column(
        children=[
            Rect(width=10, height=5, color="#f00"),
            Rect(width=20, height=10, color="#0f0"),
        ]
    )
    assert col.size(BOUNDS) == (20, 15)


def test_column_expanded_fills_height() -> None:
    """Expanded Column fills available vertical space."""
    col = Column(children=[Rect(width=10, height=5, color="#f00")], expanded=True)
    assert col.size(BOUNDS) == (10, 32)


def test_column_main_align_end(snapshot, render_widget) -> None:
    col = Column(
        children=[
            Rect(width=5, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        expanded=True,
        main_align="end",
    )
    assert render_widget(col) == snapshot


def test_column_main_align_center(snapshot, render_widget) -> None:
    col = Column(
        children=[
            Rect(width=5, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        expanded=True,
        main_align="center",
    )
    assert render_widget(col) == snapshot


def test_column_cross_align_center(snapshot, render_widget) -> None:
    col = Column(
        children=[
            Rect(width=10, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        cross_align="center",
    )
    assert render_widget(col) == snapshot


def test_column_cross_align_end(snapshot, render_widget) -> None:
    col = Column(
        children=[
            Rect(width=10, height=5, color="#f00"),
            Rect(width=5, height=5, color="#0f0"),
        ],
        cross_align="end",
    )
    assert render_widget(col) == snapshot


# --- Padding ---


@pytest.mark.parametrize(("pad", "expected"), [(2, (14, 9)), ((1, 2, 3, 4), (14, 11))])
def test_padding_adds_insets_to_child_size(pad, expected) -> None:
    padding = Padding(Rect(width=10, height=5, color="#fff"), pad=pad)
    assert padding.size(BOUNDS) == expected


def test_padding_expanded_fills_bounds() -> None:
    padding = Padding(Rect(width=10, height=5, color="#fff"), pad=2, expanded=True)
    assert padding.size(BOUNDS) == (64, 32)


def test_padding_clips_child(image, image_draw) -> None:
    padding = Padding(Rect(width=20, height=20, color="#fff"), pad=1, expanded=True)
    padding.paint(image_draw, image, (0, 0, 10, 10), 0)
    # Rect is clipped to the 10x10 bounds minus 1px padding
    assert image.getbbox() == (1, 1, 9, 9)


def test_padding_negative_clips_child(image, image_draw) -> None:
    row = Row(
        children=[
            Rect(width=5, height=5, color="#0f0"),
            Padding(Rect(width=6, height=5, color="#f00"), pad=(-3, 0, 0, 0)),
        ]
    )
    row.paint(image_draw, image, BOUNDS, 0)
    # Rect shifts 3px left under the pad; its overhang is clipped, not drawn over green
    assert image.getchannel("R").getbbox() == (5, 0, 8, 5)
    assert image.getpixel((4, 0)) == (0, 255, 0)


def test_padding_color_fills_padded_area(image, image_draw) -> None:
    padding = Padding(Rect(width=2, height=2, color="#f00"), pad=1, color="#00f")
    padding.paint(image_draw, image, BOUNDS, 0)
    assert image.getbbox() == (0, 0, 4, 4)
    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert image.getpixel((1, 1)) == (255, 0, 0)


def test_padding(snapshot, render_widget) -> None:
    col = Column(
        children=[
            Row(
                children=[
                    Padding(Rect(width=5, height=5, color="#f00"), pad=(2, 1, 3, 0)),
                    Rect(width=5, height=5, color="#0f0"),
                ]
            ),
            Row(
                children=[
                    Padding(Rect(width=5, height=5, color="#f00"), pad=1),
                    Rect(width=5, height=5, color="#0f0"),
                ]
            ),
            Padding(Rect(width=5, height=5, color="#00f"), pad=(4, 1, 0, 0)),
        ]
    )
    assert render_widget(col) == snapshot


# --- Plot ---


def test_plot_size() -> None:
    plot = Plot(data=[(0, 0), (1, 1)], width=30, height=20)
    assert plot.size(BOUNDS) == (30, 20)


def test_plot_frame_count() -> None:
    plot = Plot(data=[(0, 0), (1, 1)], width=30, height=20)
    assert plot.frame_count() == 1


def test_plot_empty_data(snapshot, render_widget) -> None:
    plot = Plot(data=[], width=30, height=20)
    assert render_widget(plot) == snapshot


def test_plot_line(snapshot, render_widget) -> None:
    data = [(float(i), float(i)) for i in range(10)]
    plot = Plot(data=data, width=30, height=20, color="#0ff")
    assert render_widget(plot) == snapshot


def test_plot_scatter(snapshot, render_widget) -> None:
    data = [(float(i), float(i % 5)) for i in range(10)]
    plot = Plot(data=data, width=30, height=20, color="#ff0", chart_type="scatter")
    assert render_widget(plot) == snapshot


def test_plot_fill(snapshot, render_widget) -> None:
    data = [(float(i), float(i)) for i in range(10)]
    plot = Plot(
        data=data, width=30, height=20, color="#0f0", fill=True, fill_color="#030"
    )
    assert render_widget(plot) == snapshot


def test_plot_with_text(snapshot, render_widget) -> None:
    """A layout combining plot and text."""
    col = Column(
        children=[
            Text(content="data", color="#fff"),
            Plot(data=[(0, 0), (5, 10), (10, 3)], width=40, height=15, color="#f00"),
        ]
    )
    assert render_widget(col) == snapshot
