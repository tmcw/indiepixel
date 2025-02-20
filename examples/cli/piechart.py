"""Render a gradient."""

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import PieChart


def render():
    """Render the widget.

    https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#piechart
    """
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    layout = PieChart(
        colors=["#fff", "#0f0", "#00f"],
        weights=[180, 135, 45],
        diameter=30,
    )

    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
