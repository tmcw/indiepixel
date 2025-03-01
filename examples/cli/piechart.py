"""Render a gradient."""

from indiepixel import PieChart


def main():
    """
    Render the widget.

    https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#piechart
    """
    return PieChart(
        colors=["#fff", "#0f0", "#00f"],
        weights=[180, 135, 45],
        diameter=30,
    )
