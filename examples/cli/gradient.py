"""Render a gradient."""

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import Box, Column, Rect, Row


def render():
    """Render the widget."""
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    layout = Box(
        Column(
            children=[
                Row(
                    children=[
                        Rect(height=16, width=1, background=(0, 0, i * 4))
                        for i in range(64)
                    ]
                ),
                Row(
                    children=[
                        Rect(height=16, width=1, background=(255 - (i * 4), 0, i * 4))
                        for i in range(64)
                    ]
                ),
            ]
        ),
        background="#000",
    )
    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
