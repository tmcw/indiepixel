import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path

import click
from flask import Flask, send_file


def create_server(mods):
    app = Flask(__name__)

    @app.route("/")
    def root() -> str:
        image_list = []
        for mod in mods:
            image_list.append(
                f"""
                <div>
                <h3>{mod[0]}</h3>
                <img style='image-rendering:pixelated;height:320px;width:640px;'  src='./image/{mod[0]}.webp' />
                </div>
                """
            )
        return f"""
            <!DOCTYPE html>
            <html>
            <head>
            <link rel="stylesheet" href="https://unpkg.com/missing.css@1.1.3">
            </head>
            <main>
            <h1>
            Indiepixel
            </h1>
            <p>
            {'\n'.join(image_list)}
            </p>
            </main>
            </html>
            """

    @app.route("/image/<path:subpath>.webp")
    def image(subpath):
        img_io = BytesIO()
        mod = [x for x in mods if x[0] == subpath]
        if len(mod) == 0:
            return f"Image not found, available modules are {map(lambda m: m[0], mods)}"
        rendered = mod[0][1].render()
        # It's very important to specify lossless=True here,
        # otherwise we get blurry output
        rendered[0].save(
            img_io,
            "WEBP",
            lossless=True,
            alpha_quality=100,
            save_all=True,
            append_images=rendered[1:],
            duration=100,
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
    if os.path.isdir(filename):
        files = Path(filename).glob("*.py")
        return [(str(p), import_from_path("render", p)) for p in files]
    return [(filename, import_from_path("render", filename))]


@click.command()
@click.argument("filename")
def cli(filename):
    mods = load_from_path(filename)
    app = create_server(mods)
    print("created app", app)
    app.run(debug=True)
