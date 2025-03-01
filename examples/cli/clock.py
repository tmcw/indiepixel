"""Render a clock."""

import datetime

import pytz

# import pytz
from indiepixel import Box, Row, Text


def main():
    """Render a clock."""
    tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(tz)
    return Box(
        Row(
            children=[
                Text(content=now.strftime("%I:%M"), color="#fff"),
            ]
        ),
        padding=2,
        background="#000",
    )
