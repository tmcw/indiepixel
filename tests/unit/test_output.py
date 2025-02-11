from __future__ import annotations

from io import BytesIO

from PIL import Image as ImagePIL
from PIL import ImageDraw

from indiepixel import Box, Row, Text

regenerate = False


def snapshot(name: str, im: ImagePIL):
    f = "PNG"
    if regenerate:
        im.save(f"tests/snapshots/{name}.png", f)
    else:
        img_io = BytesIO()
        im.save(
            img_io,
            f,
        )
        img_io.seek(0)

        with open(f"tests/snapshots/{name}.png", mode="rb") as f:
            assert f.read() == img_io.getvalue()


def test_clock() -> None:
    im = ImagePIL.new("RGB", (32, 16))
    draw = ImageDraw.Draw(im)
    layout = Box(
        Row(
            children=[
                Text("1:23AM", color="#fff"),
            ]
        ),
        padding=2,
        background="#000",
    )
    layout.paint(draw, im, (0, 0, 64, 32))
    snapshot("clock", im)
