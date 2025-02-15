"""Indiepixel's widgets and rendering logic."""

from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image as ImagePIL
from PIL import ImageColor, ImageDraw, ImageFont

type Bounds = tuple[int, int, int, int]
type Color = tuple[int, int, int] | tuple[int, int, int, int]
type InputColor = str | tuple[int, int, int] | None

fonts: dict[str, ImageFont.ImageFont] = {}

HERE = Path(__file__).resolve().parent


def initialize_fonts() -> None:
    """Load all local files and initialize them as ImageFonts."""
    files = (HERE / "fonts").glob("*.pil")
    for file in files:
        name = file.stem
        fonts[name] = ImageFont.load(str(file))


initialize_fonts()


def maybe_parse_color(color: InputColor):
    """Parse colors.

    Parse either a CSS-style color string, a (r, g, b) tuple,
    or None (transparent) into a color usable in indiepixel.
    """
    match color:
        case None:
            return None
        case str(color_str):
            return ImageColor.getrgb(color_str)
        case (r, g, b):
            return (r, g, b)


class Renderable(ABC):
    """The base class for other widgets."""

    @abstractmethod
    def paint(self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds):
        """Apply this widget to the canvas, calling paint and other methods."""

    @abstractmethod
    def measure(self, bounds: Bounds) -> tuple[int, int]:
        """Measure how large this widget will become."""


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#root
class Root(Renderable):
    """The root of the widget tree."""

    def __init__(
        self,
        *,
        child: Renderable,
        max_age: int = 100,
        delay: int = 100,
        show_full_application: bool = False,
    ) -> None:
        """Construct a root widget."""
        self.child = child
        self.max_age = max_age
        self.delay = delay
        self.show_full_application = show_full_application

    def measure(self, bounds: Bounds):
        """Return the dimensions of a widget."""
        return (64, 32)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints its child."""
        self.child.paint(
            draw,
            im,
            (
                # TODO: this hardcodes dimensions and should not.
                0,
                0,
                64,
                32,
            ),
        )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Rect(Renderable):
    """A solid-colored rectangle."""

    def __init__(
        self,
        *,
        width: int = 10,
        height: int = 10,
        background: InputColor = None,
    ) -> None:
        """Construct a rect widget."""
        self.width = width
        self.height = height
        self.background: Color | None = maybe_parse_color(background)

    def measure(self, bounds: Bounds):
        """Provide the dimensions of this rectangle."""
        return (self.width, self.height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints a rectangle."""
        draw.rectangle(
            [bounds[0], bounds[1], bounds[0] + self.width, bounds[1] + self.height],
            fill=self.background,
        )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Image(Renderable):
    """Produces an image."""

    def __init__(
        self,
        *,
        src: str,
    ) -> None:
        """Construct an image widget."""
        self.src = src
        self._image = ImagePIL.open(src)

    def measure(self, bounds: Bounds):
        """Give the measurements of the image."""
        return (self._image.width, self._image.height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Pastes an image onto the canvas."""
        im.paste(
            self._image,
            (bounds[0], bounds[1]),
        )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    """A box for another widget.

    This can provide padding
    and a background color if specified.
    """

    def __init__(
        self,
        child: Renderable,
        *,
        padding: int = 0,
        background: InputColor = None,
        expand: bool = False,
    ) -> None:
        """Construct a box widget."""
        self.child = child
        self.padding = padding
        self.background: Color | None = maybe_parse_color(background)
        self.expand = expand

    def measure(self, bounds: Bounds):
        """Measures its children and pads them if necessary."""
        if self.expand:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        (w, h) = self.child.measure(bounds)
        return (w + (self.padding * 2) + 1, h + (self.padding * 2) + 1)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints children and padding."""
        if self.expand:
            (cw, hh) = self.child.measure(bounds)
            if self.background:
                draw.rectangle(
                    [bounds[0], bounds[1], bounds[2], bounds[3]], fill=self.background
                )
            self.child.paint(
                draw,
                im,
                (
                    bounds[0] + self.padding,
                    bounds[1] + self.padding,
                    bounds[2] - self.padding,
                    bounds[3] - self.padding,
                ),
            )
        else:
            (w, h) = self.child.measure(bounds)
            if self.background:
                draw.rectangle(
                    [
                        bounds[0],
                        bounds[1],
                        bounds[0] + w + self.padding * 2,
                        bounds[1] + h + self.padding * 2,
                    ],
                    fill=self.background,
                )
            self.child.paint(
                draw,
                im,
                (
                    bounds[0] + self.padding,
                    bounds[1] + self.padding,
                    bounds[2] - self.padding,
                    bounds[3] - self.padding,
                ),
            )


class Text(Renderable):
    """Text rendered on the canvas.

    This is single-line text
    only for now.
    """

    def __init__(
        self,
        text: str,
        *,
        color: InputColor = "#fff",
        font: str = "tb-8",
    ) -> None:
        """Construct a text widget."""
        self.text = text
        self.color: Color = ImageColor.getrgb(color)
        self.font = fonts[font]

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints text."""
        draw.text((bounds[0], bounds[1]), self.text, font=self.font, fill=self.color)

    def measure(self, bounds: Bounds):
        """Measures text."""
        bbox = self.font.getbbox(self.text)
        return (bbox[2], bbox[3])


class Column(Renderable):
    """A column of widgets, laid out vertically."""

    def __init__(self, children: list[Renderable]) -> None:
        """Construct a column widget."""
        self.children = children

    def measure(self, bounds: Bounds):
        """Measures the items in the column."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure(bounds)
            width = max(cw, width)
            # NOTE: this might be an off-by-one,
            # it's pretty fuzzy right now but if
            # you omit this, you'll get overlapping items
            # if you don't change anything else.
            height = height + ch + 1
        return (width, height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints the items in the column."""
        top = bounds[1]
        for child in self.children:
            child.paint(draw, im, (bounds[0], top, bounds[2], bounds[3]))
            # Debug
            # draw.rectangle([
            #     bounds[0],
            #     top,
            #     bounds[0] + 1,
            #     top + 1
            # ], fill=(255, 0, 0, 255))
            (cw, ch) = child.measure(bounds)
            top = top + ch + 1


class Row(Renderable):
    """Produces a row of widgets, laid out horizontally."""

    def __init__(self, children: list[Renderable], *, expand: bool = False) -> None:
        """Construct a row widget."""
        self.children = children
        self.expand = expand

    def measure(self, bounds: Bounds) -> tuple[int, int]:
        """Measures the items in the row."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.measure(bounds)
            height = max(ch, height)
            width = width + cw
        if self.expand:
            return (bounds[2] - bounds[0], height)
        return (width, height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints the items in the row."""
        if self.expand:
            widths = [child.measure(bounds) for child in self.children]  # noqa: F841
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.measure(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
        else:
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.measure(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
