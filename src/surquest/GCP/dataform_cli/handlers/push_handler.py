import os
from google.cloud import dataform_v1
from google.auth import default as google_auth_default
from .dataform_handler import DataformHandler


class PushHandler(DataformHandler):
    """
    Handler class for pushing local files to a Google Cloud Dataform workspace.
    Inherits the shared client setup from DataformHandler.
    """

    @classmethod
    def get_local_files(cls, source_dir):
        """
        Recursively collects all files in the given local source directory.

        Args:
            source_dir (str): Path to the local directory to search.

        Returns:
            List[str]: Sorted list of file paths relative to source_dir.
        """
        local_files = []

        # Walk the directory tree and collect full paths
        for root, _, files in os.walk(source_dir):
            for file_ in files:
                local_file_path = os.path.join(root, file_)
                local_files.append(local_file_path)

        # Convert full paths to relative paths by removing the source_dir prefix
        local_files = [
            file_.replace(f"{source_dir}/", "") for file_ in local_files
        ]

        return sorted(local_files)

    @classmethod
    def write_file(cls, source_file, target_location, workspace_path):
        """
        Uploads a local file to the specified location in a Dataform workspace.

        Args:
            source_file (str): Local file path to read from.
            target_location (str): Relative target path in the workspace.
            workspace_path (str): Fully qualified workspace path.

        Returns:
            None
        """
        with open(source_file, "rb") as f:
            file_contents = f.read()

        request = dataform_v1.WriteFileRequest(
            workspace=workspace_path,
            path=target_location,
            contents=file_contents
        )

        response = cls.dataform_client.write_file(request=request)

    @classmethod
    def remove_file(cls, file_path, workspace_path):
        """
        Removes a file from the remote Dataform workspace.

        Args:
            file_path (str): Relative path of the file to remove.
            workspace_path (str): Fully qualified workspace path.

        Returns:
            None
        """
        request = dataform_v1.RemoveFileRequest(
            workspace=workspace_path,
            path=file_path
        )

        response = cls.dataform_client.remove_file(request=request)

    @classmethod
    def remove_directory(cls, dir_path, workspace_path):
        """
        Removes a directory from the remote Dataform workspace.

        Args:
            dir_path (str): Relative path of the directory to remove.
            workspace_path (str): Fully qualified workspace path.

        Returns:
            None
        """
        request = dataform_v1.RemoveDirectoryRequest(
            workspace=workspace_path,
            path=dir_path
        )

        response = cls.dataform_client.remove_directory(request=request)

    @classmethod
    def commit_workspace_changes(cls, workspace_path, message=None):
        """
        Commits staged changes in a Dataform workspace.

        Uses the currently authenticated user's identity for the commit author.

        Args:
            workspace_path (str): Fully qualified workspace path.
            message (str, optional): Commit message.

        Returns:
            None
        """
        default_credentials, _ = google_auth_default()

        author = dataform_v1.CommitAuthor()
        principal = default_credentials.get_cred_info().get("principal")
        author.name = principal
        author.email_address = principal

        request = dataform_v1.CommitWorkspaceChangesRequest(
            name=workspace_path,
            commit_message=message,
            author=author,
        )

        response = cls.dataform_client.commit_workspace_changes(request=request)

    @classmethod
    def push_git_commits(cls, workspace_path):
        """
        Pushes committed changes in the workspace to the linked Git repository.

        Args:
            workspace_path (str): Fully qualified workspace path.

        Returns:
            None
        """
        request = dataform_v1.PushGitCommitsRequest(name=workspace_path)
        response = cls.dataform_client.push_git_commits(request=request)
