from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO
from flask import Flask, send_file
from datetime import datetime
from os import path
import pytz
import glob
from typing import TypedDict
from typing_extensions import Unpack, NotRequired
from abc import ABC, abstractmethod

type Bounds = tuple[int, int, int, int]
type Color = tuple[int, int, int] | tuple[int, int, int, int]

fonts = {}

def initialize_fonts():
    files = glob.glob('./fonts/*.pil')
    for file in files:
        name, ext = path.splitext(path.basename(file))
        fonts[name] = ImageFont.load(file)

initialize_fonts()

def maybe_parse_color(color: str | None):
    if color:
        return ImageColor.getrgb(color)
    return None


"""The base class for other widgets."""
class Renderable(ABC):
    @abstractmethod
    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        pass

    @abstractmethod
    def measure(self, bounds: Bounds) -> tuple[int, int]:
        pass

class RectParams(TypedDict):
    """A color, anything parseable by ImageColor.getrgb"""
    background: str
    width: int
    height: int

# https://github.com/tidbyt/pixlet/blob/main/render/box.go
"""A solid-colored rectangle."""
class Rect(Renderable):
    background: Color | None = None
    padding = 0
    width = 0
    height = 0

    def __init__(self, **kwargs: Unpack[RectParams]):
        self.width = kwargs.get('width', 10)
        self.height = kwargs.get('height', 10)
        self.background = maybe_parse_color(kwargs.get('background'))

    def measure(self, bounds: Bounds):
        return (self.width, self.height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        draw.rectangle([
            bounds[0],
            bounds[1],
            bounds[0] + self.width,
            bounds[1] + self.height
        ], fill=self.background)

class BoxParams(TypedDict):
    """Padding, in pixels, for all sides"""
    padding: NotRequired[int]
    background: NotRequired[str]
    width: NotRequired[int]
    height: NotRequired[int]
    expand: NotRequired[bool]

# https://github.com/tidbyt/pixlet/blob/main/render/box.go
"""A box that contains one widget inside of it, and can have
padding and a background."""
class Box(Renderable):
    """A box for another widget, this can provide padding
    and a background color if specified."""
    background = None
    padding = 0
    expand = False

    def __init__(self, child: Renderable, **kwargs: Unpack[BoxParams]):
        self.child = child
        self.padding = kwargs.get('padding', 0)
        self.background = maybe_parse_color(kwargs.get('background'))
        self.expand = kwargs.get('expand', False)

    def measure(self, bounds: Bounds):
        if self.expand:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        (w, h) = self.child.measure(bounds)
        return (w + (self.padding * 2) + 1, h + (self.padding * 2) + 1)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        if self.expand:
            (cw, hh) = self.child.measure(bounds)
            if self.background:
                draw.rectangle([
                    bounds[0],
                    bounds[1],
                    bounds[2],
                    bounds[3]
                ], fill=self.background)
            self.child.paint(draw, (
                bounds[0] + self.padding,
                bounds[1] + self.padding,
                bounds[2] - self.padding,
                bounds[3] - self.padding
            ))
        else:
            (w, h) = self.child.measure(bounds)
            if self.background:
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
    color: NotRequired[str]

"""Text rendered on the canvas. This is single-line text
only for now."""
class Text(Renderable):
    text = ""
    font = fonts['tb-8']
    color: Color =(255, 255, 255)
    def __init__(self, text: str, **kwargs: Unpack[TextParams]):
        self.text = text
        self.color = ImageColor.getrgb(kwargs.get('color', "#fff"))
        self.font = fonts[kwargs.get('font', "tb-8")]

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        draw.text((bounds[0], bounds[1]), self.text, font=self.font, fill=self.color)

    def measure(self, bounds: Bounds):
        (l, t, w, h) = self.font.getbbox(self.text)
        return (w, h)

"""A column of widgets, laid out vertically"""
class Column(Renderable):
    children = []

    def __init__(self, children: list[Renderable]):
        self.children = children

    def measure(self, bounds: Bounds):
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure(bounds)
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
            (cw, ch) = child.measure(bounds)
            top = top + ch + 1

class RowParams(TypedDict):
    expand: NotRequired[bool]

"""A row of widgets, laid out horizontally"""
class Row(Renderable):
    children = []
    expand = False

    def __init__(self, children: list[Renderable], **kwargs: Unpack[RowParams]):
        self.children = children
        self.expand = kwargs.get('expand', False)

    def measure(self, bounds: Bounds):
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure(bounds)
            if ch > height:
                height = ch
            width = width + cw
        if self.expand:
            return (bounds[2] - bounds[0], height)
        else:
            return (width, height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        if self.expand:
            widths = []
            for child in self.children:
                widths.append(child.measure(bounds))
            left = bounds[0]
            for child in self.children:
                child.paint(draw, (left, bounds[1], bounds[2],  bounds[3]))
                (cw, ch) = child.measure(bounds)
                # todo: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
        else:
            left = bounds[0]
            for child in self.children:
                child.paint(draw, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.measure(bounds)
                # todo: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1

def render():
    frames = []
    im = Image.new("RGB", (64,32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = '1'
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    layout = Box(Column([
        Row([
            Rect(
                width=4,
                height=4,
                background="purple"
            ),
            Rect(
                width=4,
                height=4,
                background="orange"
            ),
            Rect(
                width=4,
                height=4,
                background="blue"
            )
        ], expand = True),
        Row([
            Rect(
                width=2,
                height=2,
                background="red"
            ),
            Rect(
                width=3,
                height=3,
                background="gray"
            ),
            Rect(
                width=4,
                height=4,
                background="#00f"
            )
        ]),
        Row([
            Text("6x10",
                font='6x10'
            ),
            Text("thumb",
                font='tom-thumb'
            )
        ]),
        Row([
            Rect(
                width=2,
                height=2,
                background="#f22",
            ),
            Rect(
                width=3,
                height=3,
                background="#234"
            ),
            Rect(
                width=4,
                height=4,
                background="#f00"
            ),
            Text("hi"),
            Rect(
                width=2,
                height=2,
                background="#0f0"
            ),
            Text("hi"),
            Rect(
                width=2,
                height=2,
                background="#f00"
            )
        ]),
        # Box(
        #     Row([
        #         Rect(
        #             width=4,
        #             height=4,
        #             background=(255, 55, 0, 255)
        #         ),
        #         Rect(
        #             width=8,
        #             height=8,
        #             background=(0, 55, 0, 255)
        #         ),
        #         Rect(
        #             width=10,
        #             height=10,
        #             background=(0, 55, 255, 255)
        #         )
        #     ]),
        #     background=(10, 10 ,10, 255)
        # )
    ]))
    #layout = Box(
    #        Row([
    #            Box(
    #                Text("xyz", color = (255, 255, 255, 255)),
    #                padding=2,
    #                background=(10, 10, 10, 255)
    #            ),
    #            Column([
    #                # Box(
    #                #     Row([
    #                #         Box(
    #                #             Text("yea", color = (255, 0, 0, 255)),
    #                #             padding=1
    #                #         )# ,
    #                #         # Box(
    #                #         #     Text("xxx", color = (10, 100, 0, 255)#),
    #                #         #     padding=0, background=(200, 255, #255, # 255# )
    #                #         # )
    #                #     ],
    #                #     # expand = True
    #                #     ),
    #                #     background=(200, 200, 200, 200)
    #                # ),
    #                # Box(
    #                #     Row([
    #                #         Text(now.strftime("%I:%M"), color = (255, ## 255, 0, 255)),
    #                #     ]),
    #                #     background=(0, 0, 255, 255)
    #                # ),
    #                Row([
    #                    Rect(
    #                        width=4,
    #                        height=4,
    #                        background=(255, 255, 0, 255)
    #                    ),
    #                    Rect(
    #                        width=4,
    #                        height=4,
    #                        background=(0, 0, 0, 255)
    #                    )
    #                ]),
    #                Rect(
    #                    width=4,
    #                    height=4,
    #                    background=(0, 255, 0, 255)
    #                )
    #            ]),
    #        ]),
    #        expand=True,
    #        padding=2, background=(100, 0, 0, 255)
    #    )
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


rendered = render()
# It's very important to specify lossless=True here,
# otherwise we get blurry output
rendered[0].save('output.webp', 'WEBP', lossless=True, alpha_quality=100, save_all=True, append_images=rendered[1:], duration=100)

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
