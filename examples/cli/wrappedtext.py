"""Render a gradient."""

from indiepixel import WrappedText


def main():
    """
    Render the widget.

    This matches the example in https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#stack
    Successfully matches!
    """
    return WrappedText(
        content="this is a multi-line text string",
        width=50,
        color="#fa0",
    )
