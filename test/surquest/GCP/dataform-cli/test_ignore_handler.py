import pytest
from pathlib import Path
from src.surquest.GCP.dataform_cli.ignore_handler import IgnoreHandler  # Adjust the import path if needed


class TestIgnoreHandler:
    @pytest.fixture(autouse=True)
    def setup_gitignore(self, tmp_path):
        """
        Create a temporary .gitignore file and test files in a temp directory.
        This fixture runs automatically for each test in the class.
        """
        self.base_dir = tmp_path
        self.gitignore_path = tmp_path / ".gitignore"
        self.gitignore_path.write_text("""
# Comment
*.log
build/
secret.txt
""")
        self.handler = IgnoreHandler(self.gitignore_path)

    def test_file_matching_pattern(self):
        log_file = self.base_dir / "debug.log"
        log_file.touch()

        assert self.handler.is_ignored(log_file) is True

    def test_directory_ignored(self):
        build_file = self.base_dir / "build" / "main.o"
        build_file.parent.mkdir(parents=True, exist_ok=True)
        build_file.touch()

        assert self.handler.is_ignored(build_file) is True

    def test_explicit_file_ignored(self):
        secret = self.base_dir / "secret.txt"
        secret.touch()

        assert self.handler.is_ignored(secret) is True

    def test_unmatched_file(self):
        notes = self.base_dir / "notes.md"
        notes.touch()

        assert self.handler.is_ignored(notes) is False

    def test_file_outside_gitignore_scope(self, tmp_path_factory):
        # Create a second temp dir outside of self.base_dir
        outside_dir = tmp_path_factory.mktemp("outside")
        outside_file = outside_dir / "error.log"
        outside_file.touch()

        assert self.handler.is_ignored(outside_file) is False
