"""
Title: Sidecar Cleaner
Abstract: Discovers and removes generated sidecar files (sidecar.json, findings.md).
Dependencies: dataclasses, pathlib, os, typing
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

TARGET_FILES = {"sidecar.json", "findings.md"}


@dataclass
class CleanResult:
    files_found: int
    files_deleted: int
    errors: List[tuple[Path, str]] = field(default_factory=list)


class SidecarCleaner:
    """Discovers and removes sidecar-generated files from a directory tree."""

    def __init__(self, target_files: set[str] | None = None):
        self.target_files = target_files or TARGET_FILES

    def discover_files(self, root: Path) -> List[Path]:
        """Recursively finds all target files under root.

        Continues traversal when subdirectories raise permission errors.
        """
        found: List[Path] = []
        root = root.resolve()

        for dirpath, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if filename in self.target_files:
                    found.append(Path(dirpath) / filename)

        return found

    def dry_run(self, root: Path) -> List[Path]:
        """Returns list of files that would be deleted without removing them."""
        return self.discover_files(root)

    def clean(self, root: Path) -> CleanResult:
        """Discovers and deletes target files, returning a summary result."""
        files = self.discover_files(root)
        deleted = 0
        errors: List[tuple[Path, str]] = []

        for filepath in files:
            try:
                if filepath.exists():
                    filepath.unlink()
                    deleted += 1
                else:
                    errors.append((filepath, "File not found"))
            except PermissionError as e:
                errors.append((filepath, str(e)))
            except OSError as e:
                errors.append((filepath, str(e)))

        return CleanResult(
            files_found=len(files),
            files_deleted=deleted,
            errors=errors,
        )
