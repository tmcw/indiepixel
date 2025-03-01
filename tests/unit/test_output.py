"""Tests for widgets."""

# ruff: noqa: D103
from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image as ImagePIL
from PIL import ImageDraw
from syrupy.extensions.image import PNGImageSnapshotExtension

from indiepixel import Box, Renderable, Row, Text


# Make syrupy save snapshots as individual png files
@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(PNGImageSnapshotExtension)


@pytest.fixture
def image() -> ImagePIL.Image:
    return ImagePIL.new("RGB", (32, 16))


@pytest.fixture
def image_draw(image: ImagePIL.Image) -> ImageDraw.ImageDraw:
    return ImageDraw.ImageDraw(image)


@pytest.fixture
def render_widget(image, image_draw):
    """Render a widget to PNG image data."""

    def render_widget_impl(widget: Renderable) -> bytes:
        widget.paint(image_draw, image, (0, 0, 64, 32), 0)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()
        buffer.close()
        return png_bytes

    return render_widget_impl


def test_clock(snapshot, render_widget) -> None:
    widget = Box(
        Row(
            children=[
                Text(content="1:23AM", color="#fff"),
            ]
        ),
        padding=2,
        background="#000",
    )
    assert render_widget(widget) == snapshot
