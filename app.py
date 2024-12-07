from PIL import Image, ImageDraw, ImageFont, BdfFontFile
from io import BytesIO
from flask import Flask, send_file
from datetime import datetime
import pytz
from typing import TypedDict
from typing_extensions import Unpack, NotRequired

fn = ImageFont.load('fonts/tb-8.pil')

class Renderable:
    def render(self):
        print("Do not use base renderable")

    def paint(self, draw: ImageDraw.Draw):
        print("Abstract")

    def measure(self):
        return [0, 0]

class BoxParams(TypedDict):
    padding: int
    background: tuple[int, int, int, int]
    width: NotRequired[int]
    height: NotRequired[int]

# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    background = (255, 255, 255, 0)
    padding = 0

    def __init__(self, child: Renderable, **kwargs: Unpack[BoxParams]):
        self.child = child
        self.padding = kwargs['padding']
        self.background = kwargs['background']

    def measure(self):
        return self.child.measure()

    def paint(self, draw: ImageDraw.Draw):
        (l, t, w, h) = self.measure()
        draw.rectangle([0, 0, w, h], fill=self.background)
        self.child.paint(draw)

class TextParams(TypedDict):
    font: str

class Text(Renderable):
    text = ""
    font = 'tb-8'
    def __init__(self, text: str):
        self.text = text

    def paint(self, draw: ImageDraw.Draw):
        draw.text((0, 0), self.text, font=fn, fill=(255,0,255,255))

    def measure(self):
        return fn.getbbox(self.text)

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
    render_time(draw)
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    layout = Box(Text(now.strftime("%I:%M")), padding=0, background=(100, 0, 0, 255))
    layout.paint(draw)
    # draw.text((0,0), "Hello", font=fn)
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

