"""Load darkroom.toml: where the RAW library is, where outputs go, and preview settings.

The config file is local to each machine and git-ignored, because it holds real paths.
Relative paths resolve against the config file's folder, not the current directory, so a
command gives the same result wherever it is run from. Unknown keys are rejected so a typo
fails loudly instead of silently falling back to a default.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

DEFAULT_CONFIG = Path("darkroom.toml")


class ConfigError(Exception):
    """The config file is missing or invalid."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class LibraryConfig(_Strict):
    root: Path


class OutputConfig(_Strict):
    dir: Path = Path("out")


class PreviewConfig(_Strict):
    long_edge: int = Field(default=1600, ge=64, le=1600)
    quality: int = Field(default=90, ge=1, le=100)


class Config(_Strict):
    library: LibraryConfig
    output: OutputConfig = OutputConfig()
    preview: PreviewConfig = PreviewConfig()

    @property
    def previews_dir(self) -> Path:
        return self.output.dir / "previews"

    @property
    def print_dir(self) -> Path:
        return self.output.dir / "print"


def _resolve(path: Path, base: Path) -> Path:
    return path if path.is_absolute() else (base / path).resolve()


def load_config(path: Path = DEFAULT_CONFIG) -> Config:
    """Read and validate a config file, resolving relative paths against its folder."""
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            f"{path} not found: copy darkroom.example.toml to darkroom.toml and edit it"
        ) from None
    except tomllib.TOMLDecodeError as err:
        raise ConfigError(f"{path} is not valid TOML: {err}") from None
    try:
        config = Config.model_validate(raw)
    except ValidationError as err:
        raise ConfigError(f"{path} is invalid:\n{err}") from None

    base = path.resolve().parent
    return config.model_copy(
        update={
            "library": LibraryConfig(root=_resolve(config.library.root, base)),
            "output": OutputConfig(dir=_resolve(config.output.dir, base)),
        }
    )
