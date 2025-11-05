"""File operations service with sandboxing."""
import os
from pathlib import Path
from typing import List, Dict, Any


class FileService:
    """Handles file operations within a sandboxed directory."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()

    def _validate_path(self, relative_path: str) -> Path:
        """Validate and resolve a path within base_dir.

        Raises:
            ValueError: If path escapes base_dir
        """
        # Handle both relative and absolute paths
        if os.path.isabs(relative_path):
            full_path = Path(relative_path).resolve()
        else:
            full_path = (self.base_dir / relative_path).resolve()

        # Ensure it's within base_dir
        try:
            full_path.relative_to(self.base_dir)
        except ValueError:
            raise ValueError(f"Path escapes base directory: {relative_path}")

        return full_path

    def list_files(self, relative_path: str = '') -> List[Dict[str, Any]]:
        """List files and directories at the given path.

        Returns:
            List of dicts with name, size, modtime, type
        """
        dir_path = self._validate_path(relative_path)

        if not dir_path.exists():
            raise FileNotFoundError(f"Path not found: {relative_path}")

        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {relative_path}")

        entries = []
        for entry in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
            # Skip hidden files and venv
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue

            stat = entry.stat()
            entries.append({
                'name': entry.name,
                'size': stat.st_size if entry.is_file() else 0,
                'modtime': int(stat.st_mtime),
                'type': 'dir' if entry.is_dir() else 'file'
            })

        return entries

    def read_file(self, relative_path: str) -> str:
        """Read file contents as text.

        Returns:
            File contents as string
        """
        file_path = self._validate_path(relative_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {relative_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, relative_path: str, content: str):
        """Write content to a file, creating parent directories as needed."""
        file_path = self._validate_path(relative_path)

        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file with 0644 permissions
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        os.chmod(file_path, 0o644)

    def delete_file(self, relative_path: str):
        """Delete a file."""
        file_path = self._validate_path(relative_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        if file_path.is_dir():
            raise ValueError(f"Cannot delete directory with this method: {relative_path}")

        file_path.unlink()
