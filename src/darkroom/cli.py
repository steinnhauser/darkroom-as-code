"""The darkroom command line.

The four commands are placeholders until their milestones land (see the README roadmap).
They exit with an error rather than pretending to succeed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, NoReturn

import typer

from darkroom import __version__

app = typer.Typer(
    help="Render RAW photographs from declarative, version-controlled recipes.",
    no_args_is_help=True,
    add_completion=False,
)

RecipeArg = Annotated[Path, typer.Argument(help="Recipe file (YAML).")]


def _not_yet(command: str, milestone: str) -> NoReturn:
    typer.echo(f"darkroom {command} is not implemented yet (planned for {milestone}).", err=True)
    raise typer.Exit(code=2)


def _version(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version, is_eager=True, help="Show the version."),
    ] = False,
) -> None:
    """Render RAW photographs from declarative, version-controlled recipes."""


@app.command()
def preview(recipe: RecipeArg) -> None:
    """Render a small sRGB JPEG preview of a recipe into out/previews/."""
    _not_yet("preview", "M1")


@app.command()
def compare(
    folder: Annotated[Path, typer.Argument(help="Folder of candidate recipes for one photo.")],
) -> None:
    """Render every candidate in a folder and a labelled contact sheet."""
    _not_yet("compare", "M3")


@app.command("print")
def print_(recipe: RecipeArg) -> None:
    """Render a full-resolution 16-bit print TIFF of a recipe into out/print/."""
    _not_yet("print", "M5")


@app.command()
def sheet(
    folder: Annotated[Path, typer.Argument(help="Library folder, relative to the library root.")],
) -> None:
    """Render a culling contact sheet for a folder in the RAW library."""
    _not_yet("sheet", "M3")
