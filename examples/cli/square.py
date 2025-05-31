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
                Rect(width=1, height=1, color="#f00"),
                Rect(width=2, height=2, color="#f20"),
                Rect(width=4, height=4, color="#f40"),
                Rect(width=8, height=8, color="#f60"),
                Rect(width=16, height=16, color="#f80"),
                Rect(width=32, height=32, color="#fa0"),
                Rect(width=64, height=64, color="#fc0"),
                Rect(width=128, height=128, color="#ff0"),
            ],
        ),
        size=(128, 128),
    )
