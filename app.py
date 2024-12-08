from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask import Flask, send_file
from datetime import datetime
import pytz
from typing import TypedDict
from typing_extensions import Unpack, NotRequired

type Bounds = tuple[int, int, int, int]

fn = ImageFont.load('fonts/tb-8.pil')

class Renderable:
    def render(self):
        print("Do not use base renderable")

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        print("Abstract")

    def measure(self) -> tuple[int, int]:
        return (0, 0)

class RectParams(TypedDict):
    background: tuple[int, int, int, int]
    width: int
    height: int

# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Rect(Renderable):
    background = None
    padding = 0
    width = 0
    height = 0

    def __init__(self, **kwargs: Unpack[RectParams]):
        self.width = kwargs.get('width', 10)
        self.height = kwargs.get('height', 10)
        self.background = kwargs.get('background')

    def measure(self):
        return (self.width, self.height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        draw.rectangle([
            bounds[0],
            bounds[1],
            bounds[0] + self.width,
            bounds[1] + self.height
        ], fill=self.background)

class BoxParams(TypedDict):

    padding: NotRequired[int]
    background: NotRequired[tuple[int, int, int, int]]
    width: NotRequired[int]
    height: NotRequired[int]

# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    background = None
    padding = 0

    def __init__(self, child: Renderable, **kwargs: Unpack[BoxParams]):
        self.child = child
        self.padding = kwargs.get('padding', 0)
        self.background = kwargs.get('background')

    def measure(self):
        (w, h) = self.child.measure()
        return (w + (self.padding * 2), h + (self.padding * 2))

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        (w, h) = self.child.measure()
        print(f"painting box at {bounds[0]}")
        if self.background:
            print(f"box height of {h + self.padding * 2}")
            draw.rectangle([
                bounds[0],
                bounds[1],
                bounds[0] + w + self.padding * 2,
                bounds[1] + h + self.padding * 2
            ], fill=self.background)
        self.child.paint(draw, (
            bounds[0] + self.padding,
            bounds[1] + self.padding,
            bounds[2] - self.padding,
            bounds[3] - self.padding
        ))

class TextParams(TypedDict):
    font: NotRequired[str]
    color: NotRequired[tuple[int, int, int, int]]

class Text(Renderable):
    text = ""
    font = 'tb-8'
    color = (255, 255, 255, 255)
    def __init__(self, text: str, **kwargs: Unpack[TextParams]):
        self.text = text
        self.color = kwargs.get('color', (255, 255, 255, 255))

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        draw.text((bounds[0], bounds[1]), self.text, font=fn, fill=self.color)

    def measure(self):
        (l, t, w, h) = fn.getbbox(self.text)
        print(f"text {l} {t} {w} {h}")
        return (w, h)

class Column(Renderable):
    children = []

    def __init__(self, children: list[Renderable]):
        self.children = children

    def measure(self):
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure()
            if cw > width:
                width = cw
            # NOTE: this might be an off-by-one,
            # it's pretty fuzzy right now but if
            # you omit this, you'll get overlapping items
            # if you don't change anything else.
            height = height + ch + 1
        return (width, height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        top = bounds[1]
        for child in self.children:
            child.paint(draw, (bounds[0], top, bounds[2], bounds[3]))
            # Debug
            # draw.rectangle([
            #     bounds[0],
            #     top,
            #     bounds[0] + 1,
            #     top + 1
            # ], fill=(255, 0, 0, 255))
            (cw, ch) = child.measure()
            top = top + ch + 1

class Row(Renderable):
    children = []

    def __init__(self, children: list[Renderable]):
        self.children = children

    def measure(self):
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure()
            if ch > height:
                height = ch
            width = width + cw
        return (width, height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        left = bounds[0]
        for child in self.children:
            child.paint(draw, (left, bounds[1], bounds[2], bounds[3]))
            (cw, ch) = child.measure()
            left = left + cw

def render_time(draw):
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    t = now.strftime("%I:%M")
    draw.text((0, 0), t, font=fn)

def render():
    frames = []
    im = Image.new("RGB", (64,32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = '1'
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    print("IMAGE---------------------")
    layout = Box(
            Row([
                Box(
                    Text("xyz", color = (255, 255, 255, 255)),
                    padding=2,
                    background=(10, 10, 10, 255)
                ),
                Column([
                    Box(
                        Row([
                            Box(
                                Text("yea", color = (255, 0, 0, 255)),
                                padding=0
                            ),
                            Box(
                                Text("xxx", color = (10, 100, 0, 255)),
                                padding=0, background=(200, 255, 255, 255)
                            )
                        ]),
                        background=(200, 200, 200, 200)
                    ),
                    Box(
                        Row([
                            Text(now.strftime("%I:%M"), color = (255, 255, 0, 255)),
                        ]),
                        background=(0, 0, 255, 255)
                    ),
                    Rect(
                        width=10,
                        height=6,
                        background=(255, 255, 0, 255)
                    )
                ]),
            ]),
            padding=2, background=(100, 0, 0, 255)
        )
    # layout = Box(
    #     Stack([
    #         Row([
    #             Box(
    #                 Text("yea", color = (255, 0, 0, 255)),
    #                 padding=2
    #             ),
    #             Box(
    #                 Text("xxx", color = (10, 100, 0, 255)),
    #                 padding=2, background=(200, 255, 255, 255)
    #             )
    #         ]),
    #         Row([
    #             Text(now.strftime("%I:%M"), color = (255, 255, 0, 255)),
    #         ])
    #     ]),
    #     padding=2, background=(100, 0, 0, 255)
    # )
    layout.paint(draw, (0, 0, 64, 32))
    frames.append(im)
    return frames

app = Flask(__name__)

@app.route("/")
def root():
    return "<p><img style='image-rendering:pixelated;height:320px;width:640px;' src='./image.webp' /></p>"

@app.route("/image.webp")
def image():
    img_io = BytesIO()
    rendered = render()
    # It's very important to specify lossless=True here,
    # otherwise we get blurry output
    rendered[0].save(img_io, 'WEBP', lossless=True, alpha_quality=100, save_all=True, append_images=rendered[1:], duration=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/webp')
