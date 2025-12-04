from __future__ import annotations

import pytest

from newyearscards import __version__
from newyearscards import cli as cli_mod


def test_cli_version_flag_prints_and_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        cli_mod.main(["--version"])
    # Argparse uses SystemExit(0) for --version
    assert exc.value.code == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith("newyearscards ")
    assert __version__ in out

