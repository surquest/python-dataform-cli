import os
from google.cloud import dataform_v1
from google.api_core import exceptions
from .dataform_handler import DataformHandler


class PullHandler(DataformHandler):
    """
    Handler class for pulling files and directory structures from a Google Cloud Dataform workspace.
    Inherits the Dataform API client setup from DataformHandler.
    """

    @classmethod
    def pull_file(cls, file_path, workspace_path):
        """
        Downloads the contents of a single file from a Dataform workspace.

        Args:
            file_path (str): Path of the file to retrieve (relative to workspace root).
            workspace_path (str): Fully qualified workspace path in the format:
                "projects/PROJECT_ID/locations/LOCATION/repositories/REPOSITORY_ID/workspaces/WORKSPACE_ID"

        Returns:
            bytes: The raw file content as bytes.
        """
        request = dataform_v1.ReadFileRequest(
            workspace=workspace_path,
            path=file_path
        )

        response = cls.dataform_client.read_file(request=request)
        return response.file_contents

    @classmethod
    def get_workspace_path_content(cls, workspace_path, path=None):
        """
        Lists files and subdirectories under a given path in the workspace.

        Args:
            workspace_path (str): Fully qualified workspace path.
            path (str, optional): Subdirectory path to query. If None, root directory is used.

        Returns:
            List[dataform_v1.DirectoryEntry]: Files and directories at the given path.
        """
        request = dataform_v1.QueryDirectoryContentsRequest(
            workspace=workspace_path,
            path=path
        )

        response = cls.dataform_client.query_directory_contents(request=request)
        return response.directory_entries

    @classmethod
    def get_workspace_files(cls, workspace_path, gitignore_handler=None):
        """
        Recursively retrieves all file paths in the workspace, applying .gitignore filtering if provided.

        Args:
            workspace_path (str): The workspace path to start from.
            gitignore_handler (GitignoreHandler, optional): Handler to filter out ignored paths.

        Returns:
            List[str]: Sorted list of relative file paths in the workspace.
        """
        files, directories = cls.get_workspace_path_structure(
            workspace_path=workspace_path,
            gitignore_handler=gitignore_handler
        )

        # Recursively walk through discovered directories
        while directories:
            for directory in list(directories):  # make a copy to modify the original list
                sub_files, sub_dirs = cls.get_workspace_path_structure(
                    workspace_path=workspace_path,
                    path=directory,
                    gitignore_handler=gitignore_handler
                )

                files.extend(sub_files)
                directories.extend(sub_dirs)
                directories.remove(directory)

        return sorted(files)

    @classmethod
    def get_workspace_path_structure(cls, workspace_path, path=None, gitignore_handler=None):
        """
        Retrieves immediate files and subdirectories at a given path in the workspace, with optional filtering.

        Args:
            workspace_path (str): The workspace path.
            path (str, optional): Relative path from workspace root to inspect. Defaults to root.
            gitignore_handler (GitignoreHandler, optional): Handler to check for ignored files/directories.

        Returns:
            Tuple[List[str], List[str]]: A tuple of two lists:
                - files (List[str]): Paths to files.
                - directories (List[str]): Paths to subdirectories.
        """
        files = []
        directories = []

        entries = cls.get_workspace_path_content(
            workspace_path=workspace_path,
            path=path
        )

        for entry in entries:
            is_ignored = False

            if gitignore_handler:
                # Check if the entry should be excluded based on .gitignore rules
                if entry.directory:
                    is_ignored = gitignore_handler.is_ignored(entry.directory)
                else:
                    is_ignored = gitignore_handler.is_ignored(entry.file)

            if not is_ignored:
                if entry.directory:
                    directories.append(entry.directory)
                else:
                    files.append(entry.file)

        return files, directories

    @staticmethod
    def write_file(file_path, file_contents):
        """
        Writes binary content to the specified file, creating directories if necessary.

        Args:
            file_path (str): Full local file path to write to.
            file_contents (bytes): The binary content to write to the file.
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, "wb") as f:
            f.write(file_contents)
