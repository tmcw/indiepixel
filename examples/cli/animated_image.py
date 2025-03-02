"""Render an animation."""

from indiepixel import Animation, Image
from pathlib import Path


def main():
    """
    Render the image.

    Thanks to https://itch.io/queue/c/4949099/16x16-game-assets?game_id=1441781
    asset is CC0. Buy their art!
    """
    return Image(src=Path(__file__).resolve().parent / "fireball.gif")
