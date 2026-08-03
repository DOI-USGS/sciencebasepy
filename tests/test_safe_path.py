"""Tests for path traversal protection in SbSession._safe_path.

Verifies that:
- Normal filenames work as expected (no regression)
- Relative traversal (../) is blocked
- Absolute paths are blocked
- Empty / degenerate names are rejected
- The resolved path always lands inside the destination
"""
import os
import tempfile
import pytest

from sciencebasepy.SbSession import SbSession


class TestSafePathNormalUsage:
    """Legitimate filenames must pass through unchanged."""

    def test_simple_filename(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "data.csv")
        assert result == os.path.join(str(tmp_path), "data.csv")

    def test_filename_with_spaces(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "my file (1).zip")
        assert result == os.path.join(str(tmp_path), "my file (1).zip")

    def test_filename_with_dots(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "archive.tar.gz")
        assert result == os.path.join(str(tmp_path), "archive.tar.gz")

    def test_item_id_zip(self, tmp_path):
        """Simulates get_item_files_zip usage: item['id'] + '.zip'"""
        result = SbSession._safe_path(str(tmp_path), "5f9982f1d34e9cff790bd2fe.zip")
        assert result == os.path.join(str(tmp_path), "5f9982f1d34e9cff790bd2fe.zip")

    def test_result_is_under_destination(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "report.pdf")
        assert result.startswith(str(tmp_path))


class TestSafePathRelativeTraversal:
    """Relative path traversal must be neutralized."""

    def test_single_dotdot(self, tmp_path):
        # ../secret.txt should be stripped to just secret.txt
        result = SbSession._safe_path(str(tmp_path), "../secret.txt")
        assert os.path.basename(result) == "secret.txt"
        assert result.startswith(str(tmp_path))

    def test_deep_traversal(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "../../../../etc/cron.d/evil")
        assert os.path.basename(result) == "evil"
        assert result.startswith(str(tmp_path))

    def test_traversal_with_subdir(self, tmp_path):
        # subdir/../../../etc/passwd → basename is "passwd", stays in dest
        result = SbSession._safe_path(str(tmp_path), "subdir/../../../etc/passwd")
        assert os.path.basename(result) == "passwd"
        assert result.startswith(str(tmp_path))


class TestSafePathAbsolutePaths:
    """Absolute paths must be stripped to basename and confined."""

    def test_absolute_unix_path(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "/tmp/evil.txt")
        assert os.path.basename(result) == "evil.txt"
        assert result.startswith(str(tmp_path))

    def test_absolute_with_traversal(self, tmp_path):
        result = SbSession._safe_path(str(tmp_path), "/../../../../tmp/pwned.txt")
        assert os.path.basename(result) == "pwned.txt"
        assert result.startswith(str(tmp_path))


class TestSafePathDegenerateNames:
    """Empty or degenerate filenames must raise ValueError."""

    def test_empty_string(self, tmp_path):
        with pytest.raises(ValueError, match="Unsafe or empty filename"):
            SbSession._safe_path(str(tmp_path), "")

    def test_bare_dotdot(self, tmp_path):
        with pytest.raises(ValueError, match="Unsafe or empty filename"):
            SbSession._safe_path(str(tmp_path), "..")

    def test_bare_dot(self, tmp_path):
        with pytest.raises(ValueError, match="Unsafe or empty filename"):
            SbSession._safe_path(str(tmp_path), ".")

    def test_slash_only(self, tmp_path):
        # os.path.basename("/") == "" → should reject
        with pytest.raises(ValueError, match="Unsafe or empty filename"):
            SbSession._safe_path(str(tmp_path), "/")

    def test_trailing_slash_dotdot(self, tmp_path):
        # "../" → basename is "" → should reject
        with pytest.raises(ValueError, match="Unsafe or empty filename"):
            SbSession._safe_path(str(tmp_path), "../")
