"""Indiepixel's widgets and rendering logic."""

from abc import ABC, abstractmethod
from itertools import pairwise
from pathlib import Path
from typing import Literal

from PIL import Image as ImagePIL
from PIL import ImageColor, ImageDraw, ImageEnhance, ImageFont

type Size = tuple[int, int]
type Bounds = tuple[int, int, int, int]
type Color = tuple[int, int, int] | tuple[int, int, int, int]
type InputColor = str | tuple[int, int, int] | None
type MainAlign = Literal[
    "start", "end", "center", "space_between", "space_evenly", "space_around"
]
type CrossAlign = Literal["start", "end", "center"]
type ChartType = Literal["scatter", "line"]

fonts: dict[str, ImageFont.ImageFont] = {}

DEFAULT_SIZE = (64, 32)
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
        show_full_animation: bool = False,
        size: Size = DEFAULT_SIZE,
        brightness: float = 1.0,
    ) -> None:
        """Construct a root widget."""
        self.child = child
        self.max_age = max_age
        self.delay = delay
        self.show_full_animation = show_full_animation
        self._size = size
        self.brightness = brightness

    def size(self, bounds: Bounds):
        """Return the dimensions of a widget."""
        return self._size

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
            (0, 0, self._size[0], self._size[1]),
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


def _accumulate_positions(start: float, sizes: list[int], gap: float = 0) -> list[int]:
    """Build a list of positions by accumulating sizes with optional gaps."""
    positions = []
    pos = start
    for s in sizes:
        positions.append(round(pos))
        pos += s + gap
    return positions


def distribute_space(total: int, sizes: list[int], align: MainAlign) -> list[int]:
    """Calculate starting positions for children along the main axis."""
    used = sum(sizes)
    remaining = max(total - used, 0)
    n = len(sizes)

    match align:
        case "end":
            return _accumulate_positions(remaining, sizes)
        case "center":
            return _accumulate_positions(remaining // 2, sizes)
        case "space_between":
            gap = remaining / (n - 1) if n > 1 else 0
            return _accumulate_positions(0, sizes, gap)
        case "space_evenly":
            gap = remaining / (n + 1) if n > 0 else 0
            return _accumulate_positions(gap, sizes, gap)
        case "space_around":
            gap = remaining / n if n > 0 else 0
            return _accumulate_positions(gap / 2, sizes, gap)
        case _:
            return _accumulate_positions(0, sizes)


def cross_offset(total: int, child_size: int, align: CrossAlign) -> int:
    """Calculate the offset for a child along the cross axis."""
    match align:
        case "end":
            return total - child_size
        case "center":
            return (total - child_size) // 2
        case _:
            return 0


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#column
class Column(Renderable):
    """A column of widgets, laid out vertically."""

    def __init__(
        self,
        children: list[Renderable],
        *,
        expanded: bool = False,
        main_align: MainAlign = "start",
        cross_align: CrossAlign = "start",
    ) -> None:
        """Construct a column widget."""
        self.children = children
        self.expanded = expanded
        self.main_align: MainAlign = main_align
        self.cross_align: CrossAlign = cross_align

    def size(self, bounds: Bounds):
        """Sizes the items in the column."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.size(bounds)
            width = max(cw, width)
            height = height + ch
        if self.expanded:
            return (width, bounds[3] - bounds[1])
        return (width, height)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return max([child.frame_count() for child in self.children])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the items in the column."""
        child_sizes = [child.size(bounds) for child in self.children]
        child_heights = [s[1] for s in child_sizes]
        max_width = max((s[0] for s in child_sizes), default=0)

        total_height = bounds[3] - bounds[1] if self.expanded else sum(child_heights)
        positions = distribute_space(total_height, child_heights, self.main_align)

        for i, child in enumerate(self.children):
            cw, ch = child_sizes[i]
            x_off = cross_offset(max_width, cw, self.cross_align)
            x = bounds[0] + x_off
            y = bounds[1] + positions[i]
            child.paint(draw, im, (x, y, bounds[2], bounds[3]), frame)


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#row
class Row(Renderable):
    """Produces a row of widgets, laid out horizontally."""

    def __init__(
        self,
        children: list[Renderable],
        *,
        expanded: bool = False,
        main_align: MainAlign = "start",
        cross_align: CrossAlign = "start",
        expand: bool | None = None,
    ) -> None:
        """Construct a row widget."""
        self.children = children
        self.expanded = expand if expand is not None else expanded
        self.main_align: MainAlign = main_align
        self.cross_align: CrossAlign = cross_align

    def size(self, bounds: Bounds) -> tuple[int, int]:
        """Sizes the items in the row."""
        width = 0
        height = 0
        for child in self.children:
            (cw, ch) = child.size(bounds)
            height = max(ch, height)
            width = width + cw
        if self.expanded:
            return (bounds[2] - bounds[0], height)
        return (width, height)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return max([child.frame_count() for child in self.children])

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the items in the row."""
        child_sizes = [child.size(bounds) for child in self.children]
        child_widths = [s[0] for s in child_sizes]
        max_height = max((s[1] for s in child_sizes), default=0)

        total_width = bounds[2] - bounds[0] if self.expanded else sum(child_widths)
        positions = distribute_space(total_width, child_widths, self.main_align)

        for i, child in enumerate(self.children):
            cw, ch = child_sizes[i]
            y_off = cross_offset(max_height, ch, self.cross_align)
            x = bounds[0] + positions[i]
            y = bounds[1] + y_off
            child.paint(draw, im, (x, y, bounds[2], bounds[3]), frame)


# https://github.com/tidbyt/pixlet/blob/main/docs/widgets.md#plot
class Plot(Renderable):
    """Visualizes data series as line or scatter charts."""

    def __init__(
        self,
        *,
        data: list[tuple[float, float]],
        width: int,
        height: int,
        color: InputColor = "#fff",
        color_inverted: InputColor = None,
        fill: bool = False,
        fill_color: InputColor = None,
        fill_color_inverted: InputColor = None,
        chart_type: ChartType = "line",
        x_lim: tuple[float, float] | None = None,
        y_lim: tuple[float, float] | None = None,
    ) -> None:
        """Construct a plot widget."""
        self.data = sorted(data, key=lambda p: p[0])
        self.width = width
        self.height = height
        self.color = maybe_parse_color(color) or (255, 255, 255)
        self.color_inverted = maybe_parse_color(color_inverted) or self.color
        self.fill = fill
        self.fill_color = maybe_parse_color(fill_color) or self.color
        self.fill_color_inverted = (
            maybe_parse_color(fill_color_inverted) or self.color_inverted
        )
        self.chart_type = chart_type
        self.x_lim = x_lim
        self.y_lim = y_lim

    def size(self, bounds: Bounds):
        """Return the configured width and height."""
        return (self.width, self.height)

    def frame_count(self) -> int:
        """How many frames this widget produces."""
        return 1

    def _map_point(self, x: float, y: float, bounds: Bounds) -> tuple[float, float]:
        """Map a data point to pixel coordinates."""
        x_vals = [p[0] for p in self.data]
        y_vals = [p[1] for p in self.data]
        x_min = self.x_lim[0] if self.x_lim else min(x_vals)
        x_max = self.x_lim[1] if self.x_lim else max(x_vals)
        y_min = self.y_lim[0] if self.y_lim else min(y_vals)
        y_max = self.y_lim[1] if self.y_lim else max(y_vals)

        x_range = x_max - x_min
        y_range = y_max - y_min

        px = bounds[0] + ((x - x_min) / x_range * (self.width - 1) if x_range else 0)
        py = (
            bounds[1]
            + self.height
            - 1
            - ((y - y_min) / y_range * (self.height - 1) if y_range else 0)
        )
        return (px, py)

    def paint(
        self, draw: ImageDraw.ImageDraw, im: ImagePIL.Image, bounds: Bounds, frame: int
    ) -> None:
        """Paints the plot."""
        if not self.data:
            return

        points = [self._map_point(x, y, bounds) for x, y in self.data]

        if self.fill:
            y_vals = [p[1] for p in self.data]
            y_min = self.y_lim[0] if self.y_lim else min(y_vals)
            y_max = self.y_lim[1] if self.y_lim else max(y_vals)
            y_range = y_max - y_min
            zero_y = (
                bounds[1]
                + self.height
                - 1
                - ((0 - y_min) / y_range * (self.height - 1) if y_range else 0)
            )
            zero_y = max(bounds[1], min(bounds[1] + self.height - 1, zero_y))

            for i in range(len(points) - 1):
                x0, y0 = points[i]
                x1, y1 = points[i + 1]
                for px in range(round(x0), round(x1) + 1):
                    if x1 == x0:
                        py = y0
                    else:
                        t = (px - x0) / (x1 - x0)
                        py = y0 + t * (y1 - y0)
                    orig_y = self.data[i][1]
                    fc = self.fill_color if orig_y >= 0 else self.fill_color_inverted
                    top = min(py, zero_y)
                    bottom = max(py, zero_y)
                    draw.line(
                        [(px, round(top)), (px, round(bottom))],
                        fill=fc,
                    )

        if self.chart_type == "line":
            for i in range(len(points) - 1):
                c = self.color if self.data[i][1] >= 0 else self.color_inverted
                draw.line(
                    [points[i], points[i + 1]],
                    fill=c,
                )
        else:
            for i, (px, py) in enumerate(points):
                c = self.color if self.data[i][1] >= 0 else self.color_inverted
                draw.point((round(px), round(py)), fill=c)


def render(widget: Renderable) -> list[ImagePIL.Image]:
    """Render an animated widget."""
    frames: list[ImagePIL.Image] = []

    frame_count = widget.frame_count()
    size = widget.size((0, 0, 0, 0)) if isinstance(widget, Root) else DEFAULT_SIZE
    brightness = widget.brightness if isinstance(widget, Root) else 1.0

    for frame in range(frame_count):
        im = ImagePIL.new("RGB", size)
        draw = ImageDraw.Draw(im)
        draw.fontmode = "1"
        widget.paint(draw, im, (0, 0, size[0], size[1]), frame)

        if brightness < 1.0:
            im = ImageEnhance.Brightness(im).enhance(brightness)

        frames.append(im)

    return frames
