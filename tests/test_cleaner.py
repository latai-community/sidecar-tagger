import os
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from sdk.cleaner import SidecarCleaner, CleanResult, TARGET_FILES

logging.disable(logging.CRITICAL)


@pytest.fixture
def mock_directory_tree(tmp_path):
    """Creates a nested directory structure with target and non-target files."""
    root = tmp_path / "project"
    root.mkdir()

    (root / "sidecar.json").write_text("{}")
    (root / "findings.md").write_text("# findings")
    (root / "notes.txt").write_text("keep me")

    subdir = root / "sub" / "deep"
    subdir.mkdir(parents=True)
    (subdir / "sidecar.json").write_text("{}")
    (subdir / "findings.md").write_text("# nested findings")
    (subdir / "data.csv").write_text("a,b,c")

    return root


@pytest.fixture
def empty_directory(tmp_path):
    """Creates an empty directory."""
    d = tmp_path / "empty"
    d.mkdir()
    return d


@pytest.fixture
def no_target_directory(tmp_path):
    """Creates a directory with no target files."""
    d = tmp_path / "no_targets"
    d.mkdir()
    (d / "readme.txt").write_text("readme")
    (d / "config.yaml").write_text("key: value")
    return d


class TestDiscoverFiles:
    def test_finds_all_target_files_in_nested_structure(self, mock_directory_tree):
        cleaner = SidecarCleaner()
        found = cleaner.discover_files(mock_directory_tree)

        filenames = {f.name for f in found}
        assert "sidecar.json" in filenames
        assert "findings.md" in filenames
        assert len(found) == 4

    def test_returns_empty_for_empty_directory(self, empty_directory):
        cleaner = SidecarCleaner()
        found = cleaner.discover_files(empty_directory)
        assert found == []

    def test_returns_empty_for_no_target_files(self, no_target_directory):
        cleaner = SidecarCleaner()
        found = cleaner.discover_files(no_target_directory)
        assert found == []

    def test_continues_on_permission_error(self, tmp_path):
        root = tmp_path / "restricted"
        root.mkdir()
        (root / "sidecar.json").write_text("{}")

        restricted = root / "restricted_dir"
        restricted.mkdir()
        (restricted / "findings.md").write_text("# hidden")

        cleaner = SidecarCleaner()

        with patch("os.walk") as mock_walk:
            def walk_with_error(top):
                if str(top).endswith("restricted_dir"):
                    raise PermissionError("Access denied")
                yield (str(top), ["restricted_dir"], ["sidecar.json"])
                yield (str(restricted), [], ["findings.md"])

            mock_walk.side_effect = walk_with_error
            found = cleaner.discover_files(root)

        assert len(found) >= 1


class TestDryRun:
    def test_returns_file_list(self, mock_directory_tree):
        cleaner = SidecarCleaner()
        found = cleaner.dry_run(mock_directory_tree)
        assert len(found) == 4

    def test_does_not_delete_files(self, mock_directory_tree):
        cleaner = SidecarCleaner()
        cleaner.dry_run(mock_directory_tree)

        assert (mock_directory_tree / "sidecar.json").exists()
        assert (mock_directory_tree / "findings.md").exists()


class TestClean:
    def test_deletes_all_target_files(self, mock_directory_tree):
        cleaner = SidecarCleaner()
        result = cleaner.clean(mock_directory_tree)

        assert result.files_found == 4
        assert result.files_deleted == 4
        assert len(result.errors) == 0

        assert not (mock_directory_tree / "sidecar.json").exists()
        assert not (mock_directory_tree / "findings.md").exists()

    def test_handles_permission_error(self, mock_directory_tree):
        cleaner = SidecarCleaner()

        with patch.object(Path, "unlink", side_effect=PermissionError("Access denied")):
            result = cleaner.clean(mock_directory_tree)

        assert result.files_found == 4
        assert result.files_deleted == 0
        assert len(result.errors) == 4

    def test_handles_missing_files_gracefully(self, tmp_path):
        cleaner = SidecarCleaner()
        result = cleaner.clean(tmp_path)

        assert result.files_found == 0
        assert result.files_deleted == 0
        assert len(result.errors) == 0

    def test_custom_target_files(self, tmp_path):
        (tmp_path / "custom.log").write_text("log")
        (tmp_path / "sidecar.json").write_text("{}")

        cleaner = SidecarCleaner(target_files={"custom.log"})
        result = cleaner.clean(tmp_path)

        assert result.files_found == 1
        assert result.files_deleted == 1
        assert not (tmp_path / "custom.log").exists()
        assert (tmp_path / "sidecar.json").exists()


class TestCleanResult:
    def test_default_errors_list(self):
        result = CleanResult(files_found=1, files_deleted=1)
        assert result.errors == []

    def test_with_errors(self):
        errors = [(Path("a.json"), "Permission denied")]
        result = CleanResult(files_found=2, files_deleted=1, errors=errors)
        assert len(result.errors) == 1
        assert result.errors[0][0] == Path("a.json")


class TestCLISubcommands:
    def test_process_subcommand_preserves_flags(self):
        from cli.main import create_parser
        parser = create_parser()

        args = parser.parse_args(["process", "./docs", "--level", "deep", "-v", "-o", "./out"])

        assert args.command == "process"
        assert args.inputs == ["./docs"]
        assert args.level == "deep"
        assert args.verbose is True
        assert args.output_dir == "./out"

    def test_clean_subcommand_accepts_path_and_dry_run(self):
        from cli.main import create_parser
        parser = create_parser()

        args = parser.parse_args(["clean", "-p", "./test", "-n"])

        assert args.command == "clean"
        assert args.path == "./test"
        assert args.dry_run is True

    def test_clean_subcommand_defaults(self):
        from cli.main import create_parser
        parser = create_parser()

        args = parser.parse_args(["clean"])

        assert args.command == "clean"
        assert args.path == "."
        assert args.dry_run is False

    def test_requires_subcommand(self):
        from cli.main import create_parser
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestCLIIntegration:
    def test_run_clean_dry_run(self, mock_directory_tree, capsys):
        from cli.main import run_clean
        args = MagicMock()
        args.path = str(mock_directory_tree)
        args.dry_run = True

        run_clean(args)
        captured = capsys.readouterr()

        assert "[DRY RUN]" in captured.out
        assert "sidecar.json" in captured.out
        assert "findings.md" in captured.out

        assert (mock_directory_tree / "sidecar.json").exists()

    def test_run_clean_actual_clean(self, mock_directory_tree, capsys):
        from cli.main import run_clean
        args = MagicMock()
        args.path = str(mock_directory_tree)
        args.dry_run = False

        run_clean(args)
        captured = capsys.readouterr()

        assert "Clean complete" in captured.out
        assert "Files found:" in captured.out
        assert "Files deleted:" in captured.out

        assert not (mock_directory_tree / "sidecar.json").exists()
        assert not (mock_directory_tree / "findings.md").exists()

    def test_run_clean_missing_path(self, capsys):
        from cli.main import run_clean
        args = MagicMock()
        args.path = "/nonexistent/path"
        args.dry_run = False

        with pytest.raises(SystemExit):
            run_clean(args)

    def test_run_clean_with_errors(self, tmp_path, capsys):
        from cli.main import run_clean
        (tmp_path / "sidecar.json").write_text("{}")

        args = MagicMock()
        args.path = str(tmp_path)
        args.dry_run = False

        with patch.object(Path, "unlink", side_effect=PermissionError("Denied")):
            run_clean(args)

        captured = capsys.readouterr()
        assert "Errors:" in captured.out
