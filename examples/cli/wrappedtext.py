"""Render a gradient."""

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import WrappedText


def render():
    """Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    layout = WrappedText(
        content="this is a multi-line text string",
        width=50,
        color="#fa0",
    )

    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
