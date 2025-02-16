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
    def size(self, bounds: Bounds) -> tuple[int, int]:
        """Size how large this widget will become."""


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

    def size(self, bounds: Bounds):
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
class Circle(Renderable):
    """A solid-colored circle."""

    def __init__(
        self,
        *,
        diameter: int = 10,
        color: InputColor = None,
        child: Renderable | None = None,
    ) -> None:
        """Construct a circle widget.

        If given a child, it will render that child in the center,
        with some caveats! If the child is larger than the circle itself,
        rendering can get odd.
        """
        self.child = child
        self.diameter = diameter
        self.radius = diameter / 2
        self.color: Color | None = maybe_parse_color(color)

    def size(self, bounds: Bounds):
        """Provide the dimensions of this circle, which are equal to the diameter."""
        return (self.diameter, self.diameter)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints a circle."""
        draw.circle(
            xy=[bounds[0] + self.radius, bounds[1] + self.radius],
            radius=self.radius,
            fill=self.color,
        )
        if self.child:
            child_size = self.child.size(
                (
                    bounds[0],
                    bounds[1],
                    bounds[0] + self.diameter,
                    bounds[1] + self.diameter,
                )
            )
            # offset the child box inside of this box
            pad_x = round((self.diameter - child_size[0]) / 2)
            pad_y = round((self.diameter - child_size[1]) / 2)
            self.child.paint(
                draw,
                im,
                (
                    bounds[0] + pad_x,
                    bounds[1] + pad_y,
                    bounds[0] + self.diameter - pad_y,
                    bounds[1] + self.diameter - pad_x,
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
        color: InputColor = None,
    ) -> None:
        """Construct a rect widget."""
        self.width = width
        self.height = height
        self.color: Color | None = maybe_parse_color(color)

    def size(self, bounds: Bounds):
        """Provide the dimensions of this rectangle."""
        return (self.width, self.height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints a rectangle."""
        draw.rectangle(
            [bounds[0], bounds[1], bounds[0] + self.width, bounds[1] + self.height],
            fill=self.color,
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

    def size(self, bounds: Bounds):
        """Give the sizements of the image."""
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

    def size(self, bounds: Bounds):
        """Sizes its children and pads them if necessary."""
        if self.expand:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        (w, h) = self.child.size(bounds)
        return (w + (self.padding * 2) + 1, h + (self.padding * 2) + 1)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints children and padding."""
        if self.expand:
            (cw, hh) = self.child.size(bounds)
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
            (w, h) = self.child.size(bounds)
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
        *,
        content: str,
        color: InputColor = "#fff",
        font: str = "tb-8",
    ) -> None:
        """Construct a text widget."""
        self.content = content
        self.color: Color = ImageColor.getrgb(color)
        self.font = fonts[font]

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints text."""
        draw.text((bounds[0], bounds[1]), self.content, font=self.font, fill=self.color)

    def size(self, bounds: Bounds):
        """Sizes text."""
        bbox = self.font.getbbox(self.content)
        return (bbox[2], bbox[3])


class Stack(Renderable):
    """Renders each of its children on top of each other."""

    def __init__(self, children: list[Renderable]) -> None:
        """Construct a column widget."""
        self.children = children

    def size(self, bounds: Bounds):
        """Find is the size of the largest child."""
        child_sizes = map(lambda c: c.size(bounds), self.children)

        return (
            max(map(lambda size: size[0], child_sizes)),
            max(map(lambda size: size[1], child_sizes)),
        )

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        """Paints all the items on top of each other."""
        for child in self.children:
            child.paint(draw, im, (bounds))


class Column(Renderable):
    """A column of widgets, laid out vertically."""

    def __init__(self, children: list[Renderable]) -> None:
        """Construct a column widget."""
        self.children = children

    def size(self, bounds: Bounds):
        """Sizes the items in the column."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.size(bounds)
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
            (cw, ch) = child.size(bounds)
            top = top + ch + 1


class Row(Renderable):
    """Produces a row of widgets, laid out horizontally."""

    def __init__(self, children: list[Renderable], *, expand: bool = False) -> None:
        """Construct a row widget."""
        self.children = children
        self.expand = expand

    def size(self, bounds: Bounds) -> tuple[int, int]:
        """Sizes the items in the row."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.size(bounds)
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
            widths = [child.size(bounds) for child in self.children]  # noqa: F841
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.size(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
        else:
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.size(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
