from io import BytesIO

from flask import Flask, send_file
from PIL import Image, ImageDraw

# import pytz
from indiepixel import Box, Column, Rect, Row, Text


def render():
    frames = []
    im = Image.new("RGB", (64, 32))
    draw = ImageDraw.Draw(im)
    draw.fontmode = "1"
    # tz = pytz.timezone("America/New_York")
    layout = Box(
        Column(
            [
                Row(
                    [
                        Rect(width=4, height=4, background="purple"),
                        Rect(width=4, height=4, background="orange"),
                        Rect(width=4, height=4, background="blue"),
                    ],
                    expand=True,
                ),
                Row(
                    [
                        Rect(width=2, height=2, background="red"),
                        Rect(width=3, height=3, background="gray"),
                        Rect(width=4, height=4, background="#00f"),
                    ]
                ),
                Row([Text("6x10", font="6x10"), Text("hello", font="tom-thumb")]),
                Row(
                    [
                        Rect(
                            width=2,
                            height=2,
                            background="#f22",
                        ),
                        Rect(width=3, height=3, background="#234"),
                        Rect(width=4, height=4, background="#f00"),
                        Text("hi"),
                        Rect(width=2, height=2, background="#0f0"),
                        Text("hi"),
                        Rect(width=2, height=2, background="#f00"),
                    ]
                ),
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
            ]
        )
    )
    # layout = Box(
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
    rendered[0].save(
        img_io,
        "WEBP",
        lossless=True,
        alpha_quality=100,
        save_all=True,
        append_images=rendered[1:],
        duration=100,
    )
    img_io.seek(0)
    return send_file(img_io, mimetype="image/webp")
