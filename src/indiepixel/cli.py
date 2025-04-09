"""CLI that runs an interactive server for indiepixel."""

import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path

import click
from flask import Flask, render_template, request, send_file

from indiepixel import render


def create_server(filename: str, duration: int):
    """Produce a server that will display the widgets listed by mods."""
    app = Flask(__name__)

    @app.route("/")
    def root() -> str:
        mods = load_from_path(filename)
        host = request.headers["Host"]
        return render_template("index.html", widgets=mods, host=host)

    @app.route("/widget/<path:subpath>")
    def widget(subpath) -> str:
        mods = load_from_path(filename)
        widget = next((w for w in mods if w[0] == subpath), None)
        host = request.headers["Host"]
        if widget is None:
            return render_template("not_found.html")
        return render_template("widget.html", widget=widget, host=host)

    @app.route("/image/<path:subpath>.webp")
    def image(subpath):
        mods = load_from_path(filename)
        """Display an image."""
        mod = [x for x in mods if x[0] == subpath]
        if len(mod) == 0:
            return f"Image not found, available modules are {map(lambda m: m[0], mods)}"
        frames = render(mod[0][1].main())
        # It's very important to specify lossless=True here,
        # otherwise we get blurry output
        img_io = BytesIO()
        print(frames)
        frames[0].save(
            img_io,
            "WEBP",
            lossless=True,
            alpha_quality=100,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
        )
        img_io.seek(0)
        return send_file(img_io, mimetype="image/webp")

    return app


def import_from_path(module_name, file_path):
    """Import a module given its name and file path."""
    print(f"importing {file_path}")
    spec = spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise Exception("Could not get spec")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_from_path(filename):
    """Find all python files in a path if it's a directory."""
    if os.path.isdir(filename):
        files = Path(filename).glob("*.py")
        return [(str(p), import_from_path("render", p)) for p in files]
    return [(filename, import_from_path("render", filename))]


@click.command()
@click.argument("filename")
@click.option("--duration", default=500, help="Frame duration for animations")
def cli(filename: str, duration: int):
    """Run indiepixel in a CLI."""
    app = create_server(filename, duration)
    print("created app", app)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port, host="0.0.0.0")  # noqa: S104
