"""Render a gradient."""

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import Rect, Stack, Text


def render():
    """Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    layout = Stack(
        children=[
            Rect(width=50, height=25, color="#911"),
            Text("hello there"),
            Rect(width=4, height=32, color="#119"),
        ],
    )

    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
