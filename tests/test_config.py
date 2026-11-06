from pathlib import Path

import pytest

from darkroom.config import ConfigError, load_config

EXAMPLE = Path(__file__).parent.parent / "darkroom.example.toml"


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "darkroom.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_example_config_is_valid() -> None:
    config = load_config(EXAMPLE)
    assert config.preview.long_edge == 1600
    assert config.preview.quality == 90


def test_relative_paths_resolve_against_the_config_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = write(tmp_path, '[library]\nroot = "photos"\n[output]\ndir = "renders"\n')
    monkeypatch.chdir("/")
    config = load_config(path)
    assert config.library.root == tmp_path.resolve() / "photos"
    assert config.previews_dir == tmp_path.resolve() / "renders" / "previews"
    assert config.print_dir == tmp_path.resolve() / "renders" / "print"


def test_absolute_paths_are_kept(tmp_path: Path) -> None:
    path = write(tmp_path, '[library]\nroot = "/mnt/photos"\n')
    assert load_config(path).library.root == Path("/mnt/photos")


def test_defaults_apply_when_sections_are_left_out(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, '[library]\nroot = "raw"\n'))
    assert config.output.dir == tmp_path.resolve() / "out"
    assert config.preview.long_edge == 1600


def test_missing_file_explains_how_to_create_it(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="darkroom.example.toml"):
        load_config(tmp_path / "darkroom.toml")


def test_unknown_keys_are_rejected(tmp_path: Path) -> None:
    path = write(tmp_path, '[library]\nroot = "raw"\n[preview]\nlong_egde = 1200\n')
    with pytest.raises(ConfigError, match="long_egde"):
        load_config(path)


def test_previews_cannot_exceed_1600_px(tmp_path: Path) -> None:
    path = write(tmp_path, '[library]\nroot = "raw"\n[preview]\nlong_edge = 4000\n')
    with pytest.raises(ConfigError, match="long_edge"):
        load_config(path)


def test_invalid_toml_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not valid TOML"):
        load_config(write(tmp_path, "[library\n"))
