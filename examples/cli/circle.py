"""Render a gradient."""

from indiepixel import Box, Circle


def main():
    """
    Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#circle
    Note that it's not exactly the same rendering
    because pixlet does anti-aliasing and this does
    not, currently.
    """
    return Box(
        Circle(
            color="#666",
            diameter=30,
            child=Circle(color="#0ff", diameter=10),
        ),
        background="#000",
    )
