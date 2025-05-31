"""Render an animation."""

from indiepixel import Animation, Rect, Root


def main():
    """
    Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """
    return Root(
        child=Animation(
            children=[
                Rect(width=64, height=10, color="#f00"),
                Rect(width=64, height=50, color="#f00"),
                Rect(width=64, height=90, color="#f00"),
            ],
        ),
        size=(64, 90),
    )
