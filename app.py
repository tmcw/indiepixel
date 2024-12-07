from PIL import Image, ImageDraw, ImageFont, BdfFontFile
from io import BytesIO
from flask import Flask, send_file
from datetime import datetime
import pytz

fn = ImageFont.load('fonts/tb-8.pil')

def render_time(draw):
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    t = now.strftime("%I:%M")
    draw.text((0, 0), t, font=fn)

def render():
    frames = []
    im = Image.new("RGB", (64,32))
    draw = ImageDraw.Draw(im)
    render_time(draw)
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
    rendered[0].save(img_io, 'WEBP', save_all=True, append_images=rendered[1:], duration=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/webp')

