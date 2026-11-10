"""CLI exit-code tests: failures must propagate instead of exiting 0."""
import sys
from unittest import mock

import niicat.cli as cli


def test_missing_img2sixel_returns_nonzero():
    with mock.patch.object(sys, "argv", ["niicat", "dummy.png", "-lb"]):
        with mock.patch.object(cli, "is_executable", return_value=False):
            assert cli.main() == 1


def test_display_command_failure_propagates_returncode():
    fake_result = mock.Mock(returncode=3)
    with mock.patch.object(sys, "argv", ["niicat", "dummy.png"]):
        with mock.patch("subprocess.run", return_value=fake_result) as run:
            assert cli.main() == 3
            run.assert_called_once()
