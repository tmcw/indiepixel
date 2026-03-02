"""Render a plot."""

import math

from indiepixel import Box, Plot, Root


def main():
    """Render a sine wave plot."""
    data = [(x / 4, math.sin(x / 4)) for x in range(80)]
    return Root(
        child=Box(
            Plot(
                data=data,
                width=60,
                height=28,
                color="#0ff",
                color_inverted="#f80",
                fill=True,
                fill_color="#033",
                fill_color_inverted="#330",
            ),
            padding=2,
            background="#000",
        ),
    )
