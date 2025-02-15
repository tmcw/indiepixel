"""Render a gradient."""

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import Box, Circle


def render():
    """Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#circle
    Note that it's not exactly the same rendering
    because pixlet does anti-aliasing and this does
    not, currently.
    """
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    layout = Box(
        Circle(
            color="#666",
            diameter=30,
            child=Circle(color="#0ff", diameter=10),
        ),
        background="#000",
    )
    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
