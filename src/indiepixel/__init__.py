"""Indiepixel's widgets and rendering logic."""

from abc import ABC, abstractmethod
from itertools import pairwise
from pathlib import Path
from typing import Literal

from PIL import Image as ImagePIL
from PIL import ImageColor, ImageDraw, ImageFont

type Size = tuple[int, int]
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
    """
    Parse colors.

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
    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ):
        """Apply this widget to the canvas, calling paint and other methods."""

    @abstractmethod
    def size(self, bounds: Bounds) -> Size:
        """Size how large this widget will become."""

    @abstractmethod
    def frame_count(self) -> int:
        """How many frames this widget produces."""


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

    def frame_count(self):
        """Calculate frames as childs frames."""
        return self.child.frame_count()

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
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
            frame,
        )


class PieChart(Renderable):
    """A pie chart visualization."""

    def __init__(
        self,
        *,
        diameter: int = 10,
        colors: list[InputColor],
        weights: list[float],
    ) -> None:
        """
        Construct a pie chart widget.

        Should be given a list of weights, which can be any numbers. Those
        will be normalized into slices out of the whole pie. And a list of
        colors, which should have the same length as the weights.
        """
        total_weight = sum(weights)
        if len(weights) != len(colors):
            raise Exception("Weights must have the same length as colors")
        self.weights = [360 * (weight / total_weight) for weight in weights]
        self.diameter = diameter
        self.colors = [maybe_parse_color(color) for color in colors]
        self.slices = zip(self.weights, self.colors, strict=True)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def size(self, bounds: Bounds):
        """Provide the dimensions of this circle, which are equal to the diameter."""
        return (self.diameter, self.diameter)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints a circle."""
        start = 0
        for weight, color in self.slices:
            draw.pieslice(
                xy=[
                    (bounds[0], bounds[1]),
                    (bounds[0] + self.diameter, bounds[1] + self.diameter),
                ],
                start=start,
                end=start + weight,
                fill=color,
            )
            start += weight


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
        """
        Construct a circle widget.

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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
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
                frame,
            )


def expand(size: Size, other: Size) -> Size:
    """Combine two sizes into a maximum size in both dimensions."""
    return (max(size[0], other[0]), max(size[1], other[1]))


class Animation(Renderable):
    """Animations turns a list of children into an animation, where each child is a frame.."""

    def __init__(self, *, children: list[Renderable], debug_label: str = "") -> None:
        """Construct an animation widget."""
        self.children = children
        self.debug_label = debug_label

    def size(self, bounds: Bounds):
        """Provide the dimensions of this rectangle."""
        size = (0, 0)
        for child in self.children:
            size = expand(size, child.size(bounds))
        return size

    def frame_count(self):
        """
        Calculate frames as childs frames.

        For children that are animated themselves, this will
        produce the sum of all their frame counts.
        """
        count = sum([child.frame_count() for child in self.children])
        print(f"{self.debug_label} Count={count}")
        return count

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints each child for each frame."""
        counts = [child.frame_count() for child in self.children]

        # Create a list of the overall start positions. So for example
        # if you had an input like
        # 1, 1, 1, 1
        # this would produce
        # 1, 2, 3, 4
        starts: list[int | None] = []
        accumulator = 0
        for count in counts:
            starts.append(accumulator)
            accumulator += count
        starts.append(None)

        for i, (a, b) in enumerate(pairwise(starts)):
            if a is None:
                raise Exception("This should never happen in the Animation component")
            if (frame >= a) and ((b is None) or (frame < b)):
                self.children[i].paint(draw, im, bounds, frame - a)
                return


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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
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
        src: str | Path,
    ) -> None:
        """Construct an image widget."""
        self.src = src
        self._image = ImagePIL.open(src)

    def size(self, bounds: Bounds):
        """Give the sizements of the image."""
        return (self._image.width, self._image.height)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return getattr(self._image, "n_frames", 1)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Pastes an image onto the canvas."""
        if self.frame_count() == 1:
            im.paste(
                self._image,
                (bounds[0], bounds[1]),
            )
        else:
            # TODO: maybe use alpha composite instead?
            self._image.seek(frame)
            im.paste(
                self._image,
                (bounds[0], bounds[1]),
            )


# https://github.com/tidbyt/pixlet/blob/main/render/box.go
class Box(Renderable):
    """
    A box for another widget.

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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return self.child.frame_count()

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
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
                frame,
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
                frame,
            )


class Text(Renderable):
    """
    Text rendered on the canvas.

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
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints text."""
        draw.text((bounds[0], bounds[1]), self.content, font=self.font, fill=self.color)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def size(self, bounds: Bounds):
        """Sizes text."""
        bbox = self.font.getbbox(self.content)
        return (bbox[2], bbox[3])


type WrappedTextAlign = Literal["left", "right", "center"]


class WrappedText(Renderable):
    """
    Text rendered on the canvas.

    https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#wrappedtext
    This is single-line text
    only for now.
    """

    def __init__(
        self,
        *,
        content: str,
        width: int | None = None,
        height: int | None = None,
        linespacing: int = 0,
        color: InputColor = "#fff",
        font: str = "tb-8",
        align: WrappedTextAlign = "left",
    ) -> None:
        """Construct a text widget."""
        self.content = content
        self.color: Color = ImageColor.getrgb(color)
        self.font = fonts[font]
        self.width = width
        self.height = height
        self.linespacing = linespacing
        self.align = align

    def available_width(self, bounds: Bounds):
        """Calculate the width from either the provided or inferred bbox."""
        return bounds[2] - bounds[0] if self.width is None else self.width

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def wrap_text(self, bounds: Bounds):
        """Split lines in a very naive way."""
        w = self.available_width(bounds)
        # split with no arguments splits on whitespace
        words = self.content.split()
        first_word = words[0]
        words = words[1:]
        words_with_lengths = [(word, self.font.getlength(word)) for word in words]
        space_width_px = self.font.getlength(" ")
        output_line = first_word
        output = ""
        for word, word_width_px in words_with_lengths:
            output_line_width_px = self.font.getlength(output_line)
            width_after = output_line_width_px + word_width_px + space_width_px
            if width_after > w:
                output = output_line if output == "" else f"{output}\n{output_line}"
                output_line = word
            else:
                output_line = f"{output_line} {word}"
        return f"{output}\n{output_line}"

    def size(self, bounds: Bounds):
        """Sizes wrapped text."""
        wrapped = self.wrap_text(bounds)
        bbox = self.font.getbbox(wrapped)
        return (bounds[2] - bounds[0], bbox[3])

    def multiline_width(self, wrapped: str):
        """Get the width of a multi-line string in pixels."""
        return max([self.font.getlength(line) for line in wrapped.split("\n")])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints text."""
        wrapped = self.wrap_text(bounds)
        text_width = self.multiline_width(wrapped)
        w = self.available_width(bounds)
        left_anchor = bounds[0]
        if text_width < w:
            match self.align:
                case "right":
                    left_anchor += w - text_width
                case "center":
                    left_anchor += (w - text_width) / 2
        draw.multiline_text(
            (left_anchor, bounds[1]),
            wrapped,
            font=self.font,
            fill=self.color,
            align=self.align,
            spacing=self.linespacing,
        )


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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return max([child.frame_count() for child in self.children])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints all the items on top of each other."""
        for child in self.children:
            child.paint(draw, im, (bounds), frame)


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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return max([child.frame_count() for child in self.children])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the items in the column."""
        top = bounds[1]
        for child in self.children:
            child.paint(draw, im, (bounds[0], top, bounds[2], bounds[3]), frame)
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

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return max([child.frame_count() for child in self.children])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the items in the row."""
        if self.expand:
            widths = [child.size(bounds) for child in self.children]  # noqa: F841
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]), frame)
                (cw, ch) = child.size(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1
        else:
            left = bounds[0]
            for child in self.children:
                child.paint(draw, im, (left, bounds[1], bounds[2], bounds[3]), frame)
                (cw, ch) = child.size(bounds)
                # TODO: these +1 increments are a code smell,
                # and I want to know why they aren't correct'
                left = left + cw + 1


def render(widget: Renderable) -> list[ImagePIL.Image]:
    """Render an animated widget."""
    frames: list[ImagePIL.Image] = []

    frame_count = widget.frame_count()

    for frame in range(frame_count):
        im = ImagePIL.new("RGB", (64, 32))
        draw = ImageDraw.Draw(im)
        draw.fontmode = "1"
        widget.paint(draw, im, (0, 0, 64, 32), frame)
        frames.append(im)

    return frames
