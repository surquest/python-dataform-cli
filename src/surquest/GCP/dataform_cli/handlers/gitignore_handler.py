import fnmatch
import os
from pathlib import Path

class GitignoreHandler:
    """
    A class to parse a .gitignore file and determine if specific file paths
    should be ignored based on the defined ignore patterns.

    This simplified parser handles basic .gitignore functionality, including:
    - Comment lines starting with '#'
    - Whitespace trimming
    - Simple glob-style patterns using fnmatch
    - Directory matching with trailing slashes (e.g., 'build/')

    Note:
        This does not support negation patterns (!), double-star globs (**),
        or nested .gitignore files. Use `pathspec` for full support.
    """

    def __init__(self, gitignore_path=".gitignore"):
        """
        Initializes the IgnoreHandler with a specified .gitignore file.

        Args:
            gitignore_path (str or Path): Path to the .gitignore file. Defaults to '.gitignore'.
        """
        self.gitignore_path = Path(gitignore_path)
        self.base_dir = self.gitignore_path.parent.resolve()
        self.patterns = self._load_patterns()

    def _load_patterns(self):
        """
        Loads ignore patterns from the .gitignore file.

        Returns:
            List[str]: A list of ignore patterns.
        """
        if not self.gitignore_path.exists():
            return []

        with self.gitignore_path.open("r") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]

    def _matches_pattern(self, rel_path):
        """
        Checks if the given relative path matches any of the loaded ignore patterns.

        Args:
            rel_path (str): The path relative to the .gitignore base directory.

        Returns:
            bool: True if the path matches any ignore pattern, False otherwise.
        """
        for pattern in self.patterns:
            if pattern.endswith("/"):
                if rel_path.startswith(pattern.rstrip("/")):
                    return True
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        return False

    def is_ignored(self, file_path):
        """
        Determines whether the given file path is ignored according to .gitignore rules.

        Args:
            file_path (str or Path): The file path to check.

        Returns:
            bool: True if the file is ignored, False otherwise.
        """

        return self._matches_pattern(file_path)
