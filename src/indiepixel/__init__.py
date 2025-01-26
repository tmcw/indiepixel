import glob
from abc import ABC, abstractmethod
from os import path
from typing import NotRequired, TypedDict, Unpack

from PIL import ImageColor, ImageDraw, ImageFont

type Bounds = tuple[int, int, int, int]
type Color = tuple[int, int, int] | tuple[int, int, int, int]

fonts = {}

mypath = path.abspath(path.dirname(__file__))


def relpath(p):
    return path.join(mypath, p)


def initialize_fonts() -> None:
    files = glob.glob(relpath("./fonts/*.pil"))
    for file in files:
        name, ext = path.splitext(path.basename(file))
        fonts[name] = ImageFont.load(relpath(file))


initialize_fonts()


def maybe_parse_color(color: str | None):
    if color:
        return ImageColor.getrgb(color)
    return None


class Renderable(ABC):
    """The base class for other widgets."""

    @abstractmethod
    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds):
        pass

    @abstractmethod
    def measure(self, bounds: Bounds) -> tuple[int, int]:
        pass


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#root
class RootParams(TypedDict):
    child: Renderable
    max_age: NotRequired[str]
    show_full_application: NotRequired[bool]


class Root(Renderable):
    """The root of the widget tree."""

    def __init__(self, **kwargs: Unpack[RootParams]) -> None:
        self.child = kwargs.get("child")
        self.delay = kwargs.get("delay", 100)
        self.max_age = kwargs.get("max_age", 100)
        self.show_full_application = kwargs.get("show_full_application", False)

    def measure(self, bounds: Bounds):
        return (64, 32)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
        self.child.paint(
            draw,
            (
                0,
                0,
                64,
                32,
            ),
        )


class RectParams(TypedDict):
    """A color, anything parseable by ImageColor.getrgb"""

    background: str
    width: int
    height: int


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Rect(Renderable):
    """A solid-colored rectangle."""

    def __init__(self, **kwargs: Unpack[RectParams]) -> None:
        self.width = kwargs.get("width", 10)
        self.height = kwargs.get("height", 10)
        self.background: Color | None = maybe_parse_color(kwargs.get("background"))

    def measure(self, bounds: Bounds):
        return (self.width, self.height)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
        draw.rectangle(
            [bounds[0], bounds[1], bounds[0] + self.width, bounds[1] + self.height],
            fill=self.background,
        )


class BoxParams(TypedDict):
    """Padding, in pixels, for all sides"""

    padding: NotRequired[int]
    background: NotRequired[str]
    width: NotRequired[int]
    height: NotRequired[int]
    expand: NotRequired[bool]


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    """A box for another widget, this can provide padding
    and a background color if specified."""

    def __init__(self, child: Renderable, **kwargs: Unpack[BoxParams]) -> None:
        self.child = child
        self.padding = kwargs.get("padding", 0)
        self.background: Color | None = maybe_parse_color(kwargs.get("background"))
        self.expand = kwargs.get("expand", False)

    def measure(self, bounds: Bounds):
        if self.expand:
            return (bounds[2] - bounds[0], bounds[3] - bounds[1])
        (w, h) = self.child.measure(bounds)
        return (w + (self.padding * 2) + 1, h + (self.padding * 2) + 1)

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
        if self.expand:
            (cw, hh) = self.child.measure(bounds)
            if self.background:
                draw.rectangle(
                    [bounds[0], bounds[1], bounds[2], bounds[3]], fill=self.background
                )
            self.child.paint(
                draw,
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
                (
                    bounds[0] + self.padding,
                    bounds[1] + self.padding,
                    bounds[2] - self.padding,
                    bounds[3] - self.padding,
                ),
            )


class TextParams(TypedDict):
    font: NotRequired[str]
    color: NotRequired[str]


class Text(Renderable):
    """Text rendered on the canvas. This is single-line text
    only for now.
    """

    def __init__(self, text: str, **kwargs: Unpack[TextParams]) -> None:
        self.text = text
        self.color: Color = ImageColor.getrgb(kwargs.get("color", "#fff"))
        self.font = fonts[kwargs.get("font", "tb-8")]

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
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

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
        top = bounds[1]
        for child in self.children:
            child.paint(draw, (bounds[0], top, bounds[2], bounds[3]))
            # Debug
            # draw.rectangle([
            #     bounds[0],
            #     top,
            #     bounds[0] + 1,
            #     top + 1
            # ], fill=(255, 0, 0, 255))
            (cw, ch) = child.measure(bounds)
            top = top + ch + 1


class RowParams(TypedDict):
    expand: NotRequired[bool]


class Row(Renderable):
    """A row of widgets, laid out horizontally"""

    def __init__(self, children: list[Renderable], **kwargs: Unpack[RowParams]) -> None:
        self.children = children
        self.expand = kwargs.get("expand", False)

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

    def paint(self, draw: ImageDraw.ImageDraw, bounds: Bounds) -> None:
        if self.expand:
            widths = [child.measure(bounds) for child in self.children]  # noqa: F841
            left = bounds[0]
            for child in self.children:
                child.paint(draw, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.measure(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
        else:
            left = bounds[0]
            for child in self.children:
                child.paint(draw, (left, bounds[1], bounds[2], bounds[3]))
                (cw, ch) = child.measure(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
