from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image as ImagePIL
from PIL import ImageColor, ImageDraw, ImageFont

type Bounds = tuple[int, int, int, int]
type Color = tuple[int, int, int] | tuple[int, int, int, int]

fonts: dict[str, ImageFont.ImageFont] = {}

HERE = Path(__file__).resolve().parent


def initialize_fonts() -> None:
    files = (HERE / "fonts").glob("*.pil")
    for file in files:
        name = file.stem
        fonts[name] = ImageFont.load(str(file))


initialize_fonts()


def maybe_parse_color(color: str | None):
    if color:
        return ImageColor.getrgb(color)
    return None


class Renderable(ABC):
    """The base class for other widgets."""

    @abstractmethod
    def paint(self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds):
        pass

    @abstractmethod
    def measure(self, bounds: Bounds) -> tuple[int, int]:
        pass


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
        self.child = child
        self.max_age = max_age
        self.delay = delay
        self.show_full_application = show_full_application

    def measure(self, bounds: Bounds):
        return (64, 32)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        self.child.paint(
            draw,
            im,
            (
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
        background: str | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.background: Color | None = maybe_parse_color(background)

    def measure(self, bounds: Bounds):
        return (self.width, self.height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        draw.rectangle(
            [bounds[0], bounds[1], bounds[0] + self.width, bounds[1] + self.height],
            fill=self.background,
        )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Image(Renderable):
    """An image"""

    def __init__(
        self,
        *,
        src: str,
    ) -> None:
        self.src = src
        self._image = ImagePIL.open(src)

    def measure(self, bounds: Bounds):
        return (self._image.width, self._image.height)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        im.paste(
            self._image,
            (bounds[0], bounds[1]),
        )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    """A box for another widget, this can provide padding
    and a background color if specified.
    """

    def __init__(
        self,
        child: Renderable,
        *,
        padding: int = 0,
        background: str | None = None,
        expand: bool = False,
    ) -> None:
        self.child = child
        self.padding = padding
        self.background: Color | None = maybe_parse_color(background)
        self.expand = expand

    def measure(self, bounds: Bounds):
        if self.expand:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        (w, h) = self.child.measure(bounds)
        return (w + (self.padding * 2) + 1, h + (self.padding * 2) + 1)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
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
    """Text rendered on the canvas. This is single-line text
    only for now.
    """

    def __init__(
        self,
        text: str,
        *,
        color: str = "#fff",
        font: str = "tb-8",
    ) -> None:
        self.text = text
        self.color: Color = ImageColor.getrgb(color)
        self.font = fonts[font]

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds
    ) -> None:
        draw.text((bounds[0], bounds[1]), self.text, font=self.font, fill=self.color)

    def measure(self, bounds: Bounds):
        bbox = self.font.getbbox(self.text)
        return (bbox[2], bbox[3])


class Column(Renderable):
    """A column of widgets, laid out vertically"""

    def __init__(self, children: list[Renderable]) -> None:
        self.children = children

    def measure(self, bounds: Bounds):
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
    """A row of widgets, laid out horizontally"""

    def __init__(self, children: list[Renderable], *, expand: bool = False) -> None:
        self.children = children
        self.expand = expand

    def measure(self, bounds: Bounds) -> tuple[int, int]:
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
