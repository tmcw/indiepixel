import datetime
import pytz

from PIL import Image as ImagePIL
from PIL import ImageDraw

# import pytz
from indiepixel import Box,  Row, Text


def render():
    frames = []
    im = ImagePIL.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(tz)
    layout = Box(
        Row(children=[
             Text(now.strftime("%I:%M"), color = "#fff"),
        ]),
        padding=2, background="#000"
    )
    layout.paint(draw, im, (0, 0, 64, 32))
    frames.append(im)
    return frames
