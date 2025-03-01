"""Render a bunch of stuff."""

from pathlib import Path

# import pytz
from indiepixel import Box, Column, Image, Rect, Row, Text


def main():
    """Render a bunch of stuff."""
    # tz = pytz.timezone("America/New_York")
    return Box(
        Column(
            [
                Row(
                    [
                        Image(src=str(Path("./examples/pixel-16x16.png").resolve())),
                        Rect(width=4, height=4, color="purple"),
                        Rect(width=4, height=4, color="orange"),
                        Rect(width=4, height=4, color="blue"),
                    ],
                    expand=True,
                ),
                Row(
                    [
                        Rect(width=2, height=2, color="red"),
                        Rect(width=3, height=3, color="gray"),
                        Rect(width=4, height=4, color="#00f"),
                    ]
                ),
                Row(
                    [
                        Text(content="6x10", font="6x10"),
                        Text(content="hello", font="tom-thumb"),
                    ]
                ),
                Row(
                    [
                        Rect(
                            width=2,
                            height=2,
                            color="#f22",
                        ),
                        Rect(width=3, height=3, color="#234"),
                        Rect(width=4, height=4, color="#f00"),
                        Text(content="hi"),
                        Rect(width=2, height=2, color="#0f0"),
                        Text(content="hi"),
                        Rect(width=2, height=2, color="#f00"),
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
    #                Text(content="xyz", color = (255, 255, 255, 255)),
    #                padding=2,
    #                background=(10, 10, 10, 255)
    #            ),
    #            Column([
    #                # Box(
    #                #     Row([
    #                #         Box(
    #                #             Text(content="yea", color = (255, 0, 0, 255)),
    #                #             padding=1
    #                #         )# ,
    #                #         # Box(
    #                #         #     Text(content="xxx", color = (10, 100, 0, 255)#),
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
    #                 Text(content="yea", color = (255, 0, 0, 255)),
    #                 padding=2
    #             ),
    #             Box(
    #                 Text(content="xxx", color = (10, 100, 0, 255)),
    #                 padding=2, background=(200, 255, 255, 255)
    #             )
    #         ]),
    #         Row([
    #             Text(now.strftime("%I:%M"), color = (255, 255, 0, 255)),
    #         ])
    #     ]),
    #     padding=2, background=(100, 0, 0, 255)
    # )
