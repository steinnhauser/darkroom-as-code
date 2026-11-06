import pytest
from typer.testing import CliRunner

from darkroom import __version__
from darkroom.cli import app

runner = CliRunner()


def test_help_lists_the_planned_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("preview", "compare", "print", "sheet"):
        assert command in result.output


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


@pytest.mark.parametrize("command", ["preview", "compare", "print", "sheet"])
def test_unimplemented_commands_fail_instead_of_pretending(command: str) -> None:
    result = runner.invoke(app, [command, "anything"])
    assert result.exit_code == 2
    assert "not implemented yet" in result.output
