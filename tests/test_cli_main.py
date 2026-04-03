import sys
import platform
import pytest
from unittest.mock import patch
from io import StringIO

from sidecar_tagger.cli.main import _warn_exiftool_missing


class TestWarnExiftoolMissing:
    def test_prints_warning_when_exiftool_missing(self):
        with patch("shutil.which", return_value=None):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                _warn_exiftool_missing()
                assert "WARNING: ExifTool is not installed" in mock_stderr.getvalue()

    def test_no_warning_when_exiftool_present(self):
        with patch("shutil.which", return_value="/usr/bin/exiftool"):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                _warn_exiftool_missing()
                assert mock_stderr.getvalue() == ""

    def test_includes_macos_install_hint(self):
        with patch("shutil.which", return_value=None):
            with patch("platform.system", return_value="Darwin"):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    _warn_exiftool_missing()
                    assert "brew install exiftool" in mock_stderr.getvalue()

    def test_includes_linux_install_hint(self):
        with patch("shutil.which", return_value=None):
            with patch("platform.system", return_value="Linux"):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    _warn_exiftool_missing()
                    assert "apt" in mock_stderr.getvalue() or "libimage-exiftool-perl" in mock_stderr.getvalue()

    def test_includes_windows_install_hint(self):
        with patch("shutil.which", return_value=None):
            with patch("platform.system", return_value="Windows"):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    _warn_exiftool_missing()
                    assert "winget install exiftool" in mock_stderr.getvalue()

    def test_mentions_layer_1_impact(self):
        with patch("shutil.which", return_value=None):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                _warn_exiftool_missing()
                output = mock_stderr.getvalue()
                assert "Layer 1" in output
                assert "confidence scores" in output
