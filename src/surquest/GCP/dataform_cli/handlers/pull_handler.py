import argparse
import os
from google.cloud import dataform_v1
from google.api_core import exceptions

class PullHandler:

    dataform_client = dataform_v1.DataformClient()

    def __init__(self, dataform_client, gitignore_file):
        
        self.dataform_client = dataform_client
        self.gitignore_file = gitignore_file

    @classmethod
    def get_workspace_path(cls, project_id, region, repository_id, workspace_id):

        return cls.dataform_client.workspace_path(
            project_id, 
            region,
            repository_id,
            workspace_id
        )

    @classmethod
    def pull_file(cls, file_path, workspace_path):
        """
        Pull a file from Google Cloud Dataform Repository and Workspace

        Args:
            file_path (str): The path of the file to pull
            workspace_path (str): The Google Cloud Workspace path to pull from "projects/PROJECT_ID/locations/LOCATION/repositories/REPOSITORY_ID/workspaces/WORKSPACE_ID"
        
        Returns:
            bytes: The contents of the file
        """

        request = dataform_v1.ReadFileRequest(
            workspace=workspace_path,
            path=file_path
        )

        response = cls.dataform_client.read_file(request=request)            

        return response.file_contents

    @classmethod
    def get_workspace_path_content(cls, workspace_path, path=None):

        request = dataform_v1.QueryDirectoryContentsRequest(
            workspace=workspace_path,
            path=path
        )

        response = cls.dataform_client.query_directory_contents(request=request)

        return response.directory_entries

    @classmethod
    def get_workspace_files(cls, workspace_path, gitignore_handler=None):
        
        files, directories = cls.get_workspace_path_structure(
            workspace_path=workspace_path,
            gitignore_handler=gitignore_handler
        )

        while len(directories) > 0:

            for directory in directories:

                path_files, path_directories = cls.get_workspace_path_structure(
                    workspace_path=workspace_path,
                    path=directory,
                    gitignore_handler=gitignore_handler
                )

                files.extend(path_files)
                directories.extend(path_directories)

                directories.remove(directory)

        return sorted(files)


    @classmethod
    def get_workspace_path_structure(cls, workspace_path, path=None, gitignore_handler=None):
        
        files = []
        directories = []

        path_entries = cls.get_workspace_path_content(
            workspace_path=workspace_path,
            path=path
        )

        for entry in path_entries:
            
            is_ignored = False
            
            if gitignore_handler:

                if entry.directory:

                    is_ignored = gitignore_handler.is_ignored(entry.directory)

                else:

                    is_ignored = gitignore_handler.is_ignored(entry.file)


            if is_ignored is False:
            
                if entry.directory:
                    directories.append(entry.directory)

                else:
                    files.append(entry.file)

        return files, directories

    @staticmethod
    def write_file(file_path, file_contents):
        
        # Check if the directory exists, if not create it
        directory = os.path.dirname(f"{file_path}")
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, "wb") as f:
            f.write(file_contents)










