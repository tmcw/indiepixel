"""CLI that runs an interactive server for indiepixel."""

import base64
import os
import secrets
import sys
import time
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
from types import ModuleType

import click
from flask import Flask, Response, render_template, request, send_file

from indiepixel import DEFAULT_SIZE, Root, Size, render


class IndiepixelServer:
    """Development server for previewing indiepixel widgets."""

    def __init__(
        self,
        filename: str,
        duration: int = 500,
        password: str | None = None,
    ) -> None:
        """Construct a server for the given widget file or directory."""
        self.filename = filename
        self.duration = duration
        self.password = password
        self.active_screen: str | None = None
        self.rotation_interval = 15
        self.app = Flask(__name__)
        self._register_routes()

    def _check_auth(self):
        """Check HTTP Basic Auth if a password is configured."""
        if self.password is None:
            return None
        auth = request.authorization
        if not auth or not secrets.compare_digest(auth.password or "", self.password):
            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="Indiepixel"'},
            )
        return None

    def _render_module(self, mod):
        """Render a module's main() to WebP frames and return a file response."""
        frames = render(mod[1][0].main())
        # It's very important to specify lossless=True here,
        # otherwise we get blurry output
        img_io = BytesIO()
        frames[0].save(
            img_io,
            "WEBP",
            lossless=True,
            alpha_quality=100,
            save_all=True,
            append_images=frames[1:],
            duration=self.duration,
            loop=0,
        )
        img_io.seek(0)
        return send_file(img_io, mimetype="image/webp")

    def _register_routes(self) -> None:
        """Register all Flask routes."""
        self.app.before_request(self._check_auth)
        self._register_widget_routes()
        self._register_screen_routes()

    def _register_widget_routes(self) -> None:
        """Register widget display routes."""

        @self.app.route("/")
        def root() -> str:
            mods = load_from_path(self.filename)
            host = request.headers["Host"]
            return render_template("index.html", widgets=mods, host=host)

        @self.app.route("/widget/<path:subpath>")
        def widget(subpath) -> str:
            mods = load_from_path(self.filename)
            w = next((w for w in mods if w[0] == subpath), None)
            host = request.headers["Host"]
            if w is None:
                return render_template("not_found.html")
            return render_template("widget.html", widget=w, host=host)

        @self.app.route("/image/<path:subpath>.webp")
        def image(subpath):
            """Display an image."""
            mods = load_from_path(self.filename)
            mod = [x for x in mods if x[0] == subpath]
            if len(mod) == 0:
                return "Image not found", 404
            return self._render_module(mod[0])

    def _register_screen_routes(self) -> None:
        """Register screen selection and rotation routes."""

        @self.app.route("/active.webp")
        def active_image():
            """Serve whichever screen is currently active."""
            mods = load_from_path(self.filename)
            if not mods:
                return "No widgets found", 404
            if self.active_screen:
                mod = next((m for m in mods if m[0] == self.active_screen), None)
                if mod is None:
                    mod = mods[0]
            else:
                index = int(time.time() / self.rotation_interval) % len(mods)
                mod = mods[index]
            return self._render_module(mod)

        @self.app.route("/screen", methods=["GET"])
        def get_screen():
            """Get the currently active screen."""
            return {"active_screen": self.active_screen}

        @self.app.route("/screen/<name>", methods=["POST"])
        def set_screen(name):
            """Set the active screen."""
            self.active_screen = name
            return {"active_screen": name}

    def run(self, host: str = "0.0.0.0", port: int = 5000, **kwargs) -> None:  # noqa: S104
        """Start the development server."""
        extra_files: list[str] = []
        if os.path.isdir(self.filename):
            extra_files = [str(p) for p in Path(self.filename).glob("*.py")]
        else:
            extra_files = [self.filename]
        self.app.run(host=host, port=port, extra_files=extra_files, **kwargs)


def import_from_path(module_name, file_path) -> tuple[ModuleType, Size]:
    """Import a module given its name and file path."""
    spec = spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise Exception("Could not get spec")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    m = module.main()
    size = m.size((0, 0, 0, 0)) if isinstance(m, Root) else DEFAULT_SIZE
    return (module, size)


def load_from_path(filename):
    """Find all python files in a path if it's a directory."""
    if os.path.isdir(filename):
        files = Path(filename).glob("*.py")
        return [(str(p), import_from_path("render", p)) for p in files]
    return [(filename, import_from_path("render", filename))]


def display_in_terminal(filename: str) -> None:
    """Display rendered widgets in the terminal using iTerm2 inline image protocol."""
    mods = load_from_path(filename)
    for name, (module, _size) in mods:
        frames = render(module.main())
        img_io = BytesIO()
        frames[0].save(img_io, "PNG")
        img_data = base64.b64encode(img_io.getvalue()).decode()
        print(f"\033]1337;File=inline=1;width=auto;preserveAspectRatio=1:{img_data}\a")
        print(f"  {name}")


@click.command()
@click.argument("filename")
@click.option("--duration", default=500, help="Frame duration for animations")
@click.option("--terminal", is_flag=True, help="Display in terminal instead of server")
@click.option(
    "--password",
    default=None,
    envvar="INDIEPIXEL_PASSWORD",
    help="Password for basic auth",
)
def cli(filename: str, duration: int, *, terminal: bool, password: str | None):
    """Run indiepixel in a CLI."""
    if terminal:
        display_in_terminal(filename)
        return
    server = IndiepixelServer(filename, duration, password=password)
    port = int(os.environ.get("PORT", 5000))
    server.run(debug=True, port=port)
