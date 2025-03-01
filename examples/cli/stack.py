"""Render a gradient."""

from indiepixel import Rect, Stack, Text


def main():
    """
    Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """
    return Stack(
        children=[
            Rect(width=50, height=25, color="#911"),
            Text(content="hello there"),
            Rect(width=4, height=32, color="#119"),
        ],
    )
