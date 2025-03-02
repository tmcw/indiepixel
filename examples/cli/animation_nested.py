"""Render an animation."""

from indiepixel import Animation, Rect


def main():
    """
    Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """

    return Animation(
        debug_label="Outer",
        children=[
            Rect(width=10, height=10, color="#f00"),
            Rect(width=12, height=12, color="#0ff"),
            Rect(width=14, height=14, color="#00f"),
            Animation(
                children=[
                    Rect(width=12, height=12, color="#00f"),
                    Rect(width=8, height=8, color="#00f"),
                    Rect(width=4, height=4, color="#00f"),
                    Rect(width=2, height=2, color="#00f"),
                ]
            ),
            Rect(width=16, height=16, color="#0f0"),
            Rect(width=18, height=18, color="#ff0"),
            Animation(
                children=[
                    Rect(width=12, height=12, color="#ff0"),
                    Rect(width=8, height=8, color="#ff0"),
                    Rect(width=4, height=4, color="#ff0"),
                    Rect(width=2, height=2, color="#ff0"),
                ]
            ),
        ],
    )
