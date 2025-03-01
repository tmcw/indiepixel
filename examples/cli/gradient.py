"""Render a gradient."""

from indiepixel import Box, Column, Rect, Row


def main():
    """Render the widget."""
    return Box(
        Column(
            children=[
                Row(
                    children=[
                        Rect(height=16, width=1, color=(0, 0, i * 4)) for i in range(64)
                    ]
                ),
                Row(
                    children=[
                        Rect(height=16, width=1, color=(255 - (i * 4), 0, i * 4))
                        for i in range(64)
                    ]
                ),
            ]
        ),
        background="#000",
    )
